"""Unit tests for extraction module."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import csv

from src.ecommerce_pipeline.extraction.csv import CSVExtractor
from src.ecommerce_pipeline.exceptions import ExtractionError


class TestCSVExtractor:
    """Test suite for CSVExtractor class."""
    
    # ==================== اختبارات النجاح الأساسية ====================
    
    def test_extract_success(self, temp_csv_file, sample_df):
        """Test successful CSV extraction."""
        extractor = CSVExtractor(temp_csv_file)
        df = extractor.extract()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_df)
        assert list(df.columns) == list(sample_df.columns)
        assert not df.empty
    
    def test_extract_with_custom_columns(self, temp_csv_file):
        """Test extraction with specific columns."""
        extractor = CSVExtractor(temp_csv_file)
        df = extractor.extract()
        
        expected_cols = ['order_id', 'customer_id', 'order_date', 
                        'product_id', 'quantity', 'price', 'total']
        
        for col in expected_cols:
            assert col in df.columns
    
    def test_extract_data_types(self, temp_csv_file):
        """Test extracted data types."""
        extractor = CSVExtractor(temp_csv_file)
        df = extractor.extract()
        
        # Check numeric columns
        assert pd.api.types.is_numeric_dtype(df['quantity'])
        assert pd.api.types.is_numeric_dtype(df['price'])
        assert pd.api.types.is_numeric_dtype(df['total'])
        
        # Check string columns
        assert pd.api.types.is_object_dtype(df['order_id'])
        assert pd.api.types.is_object_dtype(df['customer_id'])
        assert pd.api.types.is_object_dtype(df['product_id'])
    
    def test_extract_returns_dataframe(self, temp_csv_file):
        """Test that extract returns a pandas DataFrame."""
        extractor = CSVExtractor(temp_csv_file)
        df = extractor.extract()
        
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] > 0
        assert df.shape[1] > 0
    
    # ==================== اختبارات الأخطاء ====================
    
    def test_extract_file_not_found(self):
        """Test extraction with missing file raises ExtractionError."""
        extractor = CSVExtractor(Path("nonexistent_file.csv"))
        
        with pytest.raises(ExtractionError) as excinfo:
            extractor.extract()
        
        assert "File not found" in str(excinfo.value)
    
    def test_extract_empty_file(self, tmp_path):
        """Test extraction with empty CSV file."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        
        extractor = CSVExtractor(empty_file)
        
        # Should raise error because no columns found
        with pytest.raises(ExtractionError):
            extractor.extract()
    
    def test_extract_file_with_only_header(self, tmp_path):
        """Test extraction with CSV file containing only header."""
        header_file = tmp_path / "header_only.csv"
        header_file.write_text("order_id,customer_id,order_date,product_id,quantity,price,total\n")
        
        extractor = CSVExtractor(header_file)
        df = extractor.extract()
        
        # Should return empty DataFrame with correct columns
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ['order_id', 'customer_id', 'order_date', 
                                    'product_id', 'quantity', 'price', 'total']
    
    # ==================== اختبارات البيانات غير المنتظمة ====================
    
    def test_extract_with_missing_values(self, tmp_path):
        """Test extraction with missing values."""
        missing_csv = tmp_path / "missing.csv"
        missing_csv.write_text("""
order_id,customer_id,order_date,product_id,quantity,price,total
ORD001,CUST001,2024-01-15,PROD001,2,,100.00
ORD002,CUST002,2024-01-16,PROD002,1,75.00,
ORD003,CUST001,,PROD003,3,30.00,90.00
""")
        
        extractor = CSVExtractor(missing_csv)
        df = extractor.extract()
        
        # Should handle missing values as NaN
        assert pd.isna(df['price'][0])
        assert pd.isna(df['total'][1])
        assert pd.isna(df['order_date'][2])
        assert len(df) == 3
    
    def test_extract_with_malformed_data(self, tmp_path):
        """Test extraction with malformed CSV data."""
        malformed = tmp_path / "malformed.csv"
        malformed.write_text("""
order_id,customer_id,order_date,product_id,quantity,price,total
ORD001,CUST001,2024-01-15,PROD001,two,50.00,100.00
""")
        
        extractor = CSVExtractor(malformed)
        df = extractor.extract()
        
        # Should still return DataFrame with mixed types
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
    
    def test_extract_with_mixed_types(self, tmp_path):
        """Test extraction with mixed data types."""
        mixed = tmp_path / "mixed.csv"
        mixed.write_text("""
order_id,customer_id,order_date,product_id,quantity,price,total
ORD001,CUST001,2024-01-15,PROD001,2,50.00,100.00
ORD002,CUST002,2024-01-16,PROD002,1,75.5,75.50
""")
        
        extractor = CSVExtractor(mixed)
        df = extractor.extract()
        
        assert len(df) == 2
        assert df['price'][1] == 75.5
    
    def test_extract_with_special_characters(self, tmp_path):
        """Test extraction with special characters in data."""
        special = tmp_path / "special.csv"
        special.write_text("""
order_id,customer_id,order_date,product_id,quantity,price,total
ORD-001,CUST_001,2024-01-15,PROD@001,2,50.00,100.00
ORD#002,CUST$002,2024-01-16,PROD%002,1,75.00,75.00
""")
        
        extractor = CSVExtractor(special)
        df = extractor.extract()
        
        assert len(df) == 2
        assert df['order_id'][0] == 'ORD-001'
        assert df['customer_id'][0] == 'CUST_001'
    
    def test_extract_with_unicode(self, tmp_path):
        """Test extraction with Unicode characters."""
        unicode_csv = tmp_path / "unicode.csv"
        unicode_csv.write_text("""
order_id,customer_id,order_date,product_id,quantity,price,total
ORD001,عميل001,2024-01-15,منتج001,2,50.00,100.00
ORD002,عميل002,2024-01-16,منتج002,1,75.00,75.00
""", encoding='utf-8')
        
        extractor = CSVExtractor(unicode_csv)
        df = extractor.extract()
        
        assert len(df) == 2
        assert df['customer_id'][0] == 'عميل001'
        assert df['product_id'][0] == 'منتج001'
    
    # ==================== اختبارات الأعمدة الإضافية ====================
    
    def test_extract_with_extra_columns(self, tmp_path):
        """Test extraction with extra columns."""
        extra = tmp_path / "extra.csv"
        extra.write_text("""
order_id,customer_id,order_date,product_id,quantity,price,total,extra_col,another_col
ORD001,CUST001,2024-01-15,PROD001,2,50.00,100.00,extra_value,another_value
""")
        
        extractor = CSVExtractor(extra)
        df = extractor.extract()
        
        # Should include extra columns
        assert 'extra_col' in df.columns
        assert 'another_col' in df.columns
        assert df['extra_col'][0] == 'extra_value'
        assert len(df.columns) == 9
    
    def test_extract_with_missing_columns(self, tmp_path):
        """Test extraction with missing required columns."""
        missing_cols = tmp_path / "missing_cols.csv"
        missing_cols.write_text("""
order_id,customer_id,order_date,product_id,quantity,price
ORD001,CUST001,2024-01-15,PROD001,2,50.00
""")
        
        extractor = CSVExtractor(missing_cols)
        df = extractor.extract()
        
        # Should still extract, but 'total' column will be missing
        assert 'total' not in df.columns
        assert len(df.columns) == 6
    
    # ==================== اختبارات الأداء ====================
    
    def test_extract_large_file(self, large_df, tmp_path):
        """Test extraction with large file (1K rows)."""
        csv_path = tmp_path / "large_orders.csv"
        large_df.to_csv(csv_path, index=False)
        
        import time
        start = time.time()
        
        extractor = CSVExtractor(csv_path)
        df = extractor.extract()
        
        elapsed = time.time() - start
        
        assert len(df) == len(large_df)
        assert elapsed < 5  # Should complete within 5 seconds
        print(f"⏱️ Extracted {len(df)} rows in {elapsed:.2f} seconds")
    
    def test_extract_performance_comparison(self, tmp_path):
        """Test extraction performance with different file sizes."""
        import time
        
        sizes = [100, 500]
        results = {}
        
        for n in sizes:
            # Generate test data
            df = pd.DataFrame({
                'id': list(range(n)),
                'value': np.random.randn(n).tolist(),
                'category': np.random.choice(['A', 'B', 'C'], n).tolist()
            })
            
            csv_path = tmp_path / f"perf_{n}.csv"
            df.to_csv(csv_path, index=False)
            
            start = time.time()
            extractor = CSVExtractor(csv_path)
            result = extractor.extract()
            elapsed = time.time() - start
            
            results[n] = elapsed
            assert len(result) == n
            
            print(f"📊 {n} rows: {elapsed:.4f} seconds")
        
        # Check that larger files take proportionally more time
        if len(results) >= 2:
            assert results[500] > results[100]