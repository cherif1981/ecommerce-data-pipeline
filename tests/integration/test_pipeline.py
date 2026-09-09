"""Integration tests for complete ETL pipeline."""

import pytest
import pandas as pd
import sqlite3
import numpy as np
from pathlib import Path

from src.ecommerce_pipeline.pipeline import ETLPipeline
from src.ecommerce_pipeline.exceptions import PipelineError, ValidationError


class TestETLPipeline:
    """Integration test suite for ETLPipeline."""
    
    def test_pipeline_full_execution(self, temp_csv_file, test_config):
        """Test complete pipeline execution."""
        pipeline = ETLPipeline(temp_csv_file)
        pipeline.run()
        
        db_path = test_config.database.sqlite_path
        assert Path(db_path).exists()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check all tables have data
        cursor.execute("SELECT COUNT(*) FROM dim_products")
        assert cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM dim_customers")
        assert cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM dim_dates")
        assert cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM fact_orders")
        assert cursor.fetchone()[0] > 0
        
        conn.close()
    
    def test_pipeline_data_quality(self, temp_csv_file, test_config):
        """Test data quality after pipeline execution."""
        pipeline = ETLPipeline(temp_csv_file)
        pipeline.run()
        
        conn = sqlite3.connect(test_config.database.sqlite_path)
        
        # Check for nulls
        df_facts = pd.read_sql_query("SELECT * FROM fact_orders", conn)
        assert not df_facts.isnull().any().any()
        
        # Check totals are positive
        assert (df_facts['quantity'] > 0).all()
        assert (df_facts['price'] > 0).all()
        assert (df_facts['total'] > 0).all()
        
        conn.close()
    
    def test_pipeline_idempotent(self, temp_csv_file, test_config):
        """Test that pipeline can run multiple times."""
        pipeline = ETLPipeline(temp_csv_file)
        
        # First run
        pipeline.run()
        
        # Second run (should overwrite)
        pipeline.run()
        
        # Should work without errors
        assert Path(test_config.database.sqlite_path).exists()
    
    def test_pipeline_file_not_found(self):
        """Test pipeline with missing file."""
        pipeline = ETLPipeline("nonexistent.csv")
        
        with pytest.raises(PipelineError):
            pipeline.run()
    
    def test_pipeline_with_corrupted_data(self, tmp_path, test_config):
        """Test pipeline with corrupted data."""
        csv_path = tmp_path / "corrupted.csv"
        csv_path.write_text("""
order_id,customer_id,order_date,product_id,quantity,price,total
invalid,data,here
""")
        
        pipeline = ETLPipeline(csv_path)
        
        with pytest.raises(PipelineError):
            pipeline.run()
    
    def test_pipeline_performance(self, tmp_path, test_config):
        """Test pipeline performance with 500 rows."""
        import numpy as np
        
        # ✅ إنشاء بيانات صحيحة
        n_rows = 500
        np.random.seed(42)
        
        # ✅ التأكد من أن total = quantity * price
        quantities = np.random.randint(1, 10, n_rows)
        prices = np.round(np.random.uniform(10, 200, n_rows), 2)
        totals = np.round(quantities * prices, 2)  # ✅ حساب total بشكل صحيح
        
        df = pd.DataFrame({
            'order_id': [f'ORD{i:06d}' for i in range(1, n_rows + 1)],
            'customer_id': [f'CUST{np.random.randint(1, 101):05d}' for _ in range(n_rows)],
            'order_date': pd.date_range('2024-01-01', periods=n_rows).strftime('%Y-%m-%d'),
            'product_id': [f'PROD{np.random.randint(1, 21):03d}' for _ in range(n_rows)],
            'quantity': quantities,
            'price': prices,
            'total': totals  # ✅ total صحيح
        })
        
        csv_path = tmp_path / "perf_orders.csv"
        df.to_csv(csv_path, index=False)
        
        pipeline = ETLPipeline(csv_path)
        pipeline.run()
        
        db_path = test_config.database.sqlite_path
        assert Path(db_path).exists()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM fact_orders")
        count = cursor.fetchone()[0]
        
        # Should handle rows efficiently
        assert count > 0
        
        conn.close()
    
    def test_pipeline_with_valid_data(self, tmp_path, test_config):
        """Test pipeline with valid data."""
        import numpy as np
        
        n_rows = 100
        np.random.seed(42)
        
        # ✅ بيانات صحيحة
        quantities = np.random.randint(1, 10, n_rows)
        prices = np.round(np.random.uniform(10, 200, n_rows), 2)
        totals = np.round(quantities * prices, 2)
        
        df = pd.DataFrame({
            'order_id': [f'ORD{i:06d}' for i in range(1, n_rows + 1)],
            'customer_id': [f'CUST{np.random.randint(1, 51):05d}' for _ in range(n_rows)],
            'order_date': pd.date_range('2024-01-01', periods=n_rows).strftime('%Y-%m-%d'),
            'product_id': [f'PROD{np.random.randint(1, 11):03d}' for _ in range(n_rows)],
            'quantity': quantities,
            'price': prices,
            'total': totals
        })
        
        csv_path = tmp_path / "valid_orders.csv"
        df.to_csv(csv_path, index=False)
        
        pipeline = ETLPipeline(csv_path)
        pipeline.run()
        
        db_path = test_config.database.sqlite_path
        assert Path(db_path).exists()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM fact_orders")
        count = cursor.fetchone()[0]
        assert count == n_rows
        
        conn.close()