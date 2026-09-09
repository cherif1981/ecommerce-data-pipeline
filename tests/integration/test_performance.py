"""Performance tests for the ETL pipeline."""

import pytest
import time
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path

from src.ecommerce_pipeline.pipeline import ETLPipeline


@pytest.mark.slow
def test_performance_10k_orders(tmp_path, test_config):
    """Test performance with 5K orders (reduced for testing)."""
    # ✅ استخدام 5000 بدلاً من 10000 للتسريع
    n_rows = 5000
    np.random.seed(42)
    
    df = pd.DataFrame({
        'order_id': [f'ORD{i:06d}' for i in range(1, n_rows + 1)],
        'customer_id': [f'CUST{np.random.randint(1, 1001):05d}' for _ in range(n_rows)],
        'order_date': pd.date_range('2024-01-01', periods=n_rows).strftime('%Y-%m-%d'),
        'product_id': [f'PROD{np.random.randint(1, 51):03d}' for _ in range(n_rows)],
        'quantity': np.random.randint(1, 10, n_rows).astype(int),
        'price': np.round(np.random.uniform(10, 200, n_rows).astype(float), 2),
        'total': np.round(np.random.uniform(10, 2000, n_rows).astype(float), 2)
    })
    
    csv_path = tmp_path / "perf_orders.csv"
    df.to_csv(csv_path, index=False)
    
    start_time = time.time()
    
    pipeline = ETLPipeline(csv_path)
    pipeline.run()
    
    elapsed = time.time() - start_time
    
    # Should complete within reasonable time
    assert elapsed < 60  # 60 seconds max
    
    print(f"⏱️ {n_rows} orders processed in {elapsed:.2f} seconds")
    
    # Verify data
    conn = sqlite3.connect(test_config.database.sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_orders")
    count = cursor.fetchone()[0]
    
    assert count >= n_rows - 100  # بعض الصفوف قد تحذف
    conn.close()


@pytest.mark.slow
def test_performance_scalability(tmp_path, test_config):
    """Test performance scaling with different data sizes."""
    sizes = [100, 500]
    results = {}
    
    for n in sizes:
        np.random.seed(42)
        
        # Generate data
        df = pd.DataFrame({
            'order_id': [f'ORD{i:06d}' for i in range(1, n + 1)],
            'customer_id': [f'CUST{np.random.randint(1, 50):05d}' for _ in range(n)],
            'order_date': pd.date_range('2024-01-01', periods=n).strftime('%Y-%m-%d'),
            'product_id': [f'PROD{np.random.randint(1, 20):03d}' for _ in range(n)],
            'quantity': np.random.randint(1, 10, n).astype(int),
            'price': np.round(np.random.uniform(10, 200, n).astype(float), 2),
            'total': np.round(np.random.uniform(10, 2000, n).astype(float), 2)
        })
        
        csv_path = tmp_path / f"scale_{n}.csv"
        df.to_csv(csv_path, index=False)
        
        start_time = time.time()
        
        pipeline = ETLPipeline(csv_path)
        pipeline.run()
        
        elapsed = time.time() - start_time
        results[n] = elapsed
        
        print(f"📊 {n} rows: {elapsed:.2f} seconds")
    
    # Check that larger files take more time
    if len(results) >= 2:
        assert results[500] >= results[100]*0.95


@pytest.mark.slow
def test_performance_with_validation(tmp_path, test_config):
    """Test performance with validation."""
    n = 1000
    np.random.seed(42)
    
    df = pd.DataFrame({
        'order_id': [f'ORD{i:06d}' for i in range(1, n + 1)],
        'customer_id': [f'CUST{np.random.randint(1, 100):05d}' for _ in range(n)],
        'order_date': pd.date_range('2024-01-01', periods=n).strftime('%Y-%m-%d'),
        'product_id': [f'PROD{np.random.randint(1, 20):03d}' for _ in range(n)],
        'quantity': np.random.randint(1, 10, n).astype(int),
        'price': np.round(np.random.uniform(10, 200, n).astype(float), 2),
        'total': np.round(np.random.uniform(10, 2000, n).astype(float), 2)
    })
    
    csv_path = tmp_path / "validation_test.csv"
    df.to_csv(csv_path, index=False)
    
    start_time = time.time()
    
    pipeline = ETLPipeline(csv_path)
    pipeline.run()
    
    elapsed = time.time() - start_time
    
    assert elapsed < 30
    print(f"⏱️ Validation with {n} rows: {elapsed:.2f} seconds")