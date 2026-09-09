"""Pytest configuration and fixtures for all tests."""

import pytest
import pandas as pd
import numpy as np
import sqlite3
import tempfile
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ecommerce_pipeline.config import get_config, reset_config
from src.ecommerce_pipeline.extraction.csv import CSVExtractor
from src.ecommerce_pipeline.validation.orders import OrderValidator
from src.ecommerce_pipeline.transformation.orders import OrderTransformer
from src.ecommerce_pipeline.loading.postgres import DatabaseLoader


@pytest.fixture
def sample_data():
    """Return sample order data."""
    return {
        'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
        'customer_id': ['CUST001', 'CUST002', 'CUST001', 'CUST003', 'CUST002'],
        'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
        'product_id': ['PROD001', 'PROD002', 'PROD003', 'PROD001', 'PROD004'],
        'quantity': [2, 1, 3, 1, 2],
        'price': [50.00, 75.00, 30.00, 50.00, 40.00],
        'total': [100.00, 75.00, 90.00, 50.00, 80.00]
    }


@pytest.fixture
def sample_df(sample_data):
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(sample_data)


@pytest.fixture
def large_df():
    """Create a large DataFrame with 10K rows for testing."""
    np.random.seed(42)
    n_rows = 1000  # ✅ تقليل عدد الصفوف لتسريع الاختبارات
    
    # ✅ إنشاء بيانات مع أنواع Python الصحيحة
    quantities = np.random.randint(1, 10, n_rows).tolist()
    prices = np.round(np.random.uniform(10, 200, n_rows), 2).tolist()
    totals = [round(q * p, 2) for q, p in zip(quantities, prices)]
    
    order_ids = [f'ORD{i:06d}' for i in range(1, n_rows + 1)]
    customer_ids = [f'CUST{np.random.randint(1, 1001):05d}' for _ in range(n_rows)]
    product_ids = [f'PROD{np.random.randint(1, 51):03d}' for _ in range(n_rows)]
    
    # ✅ إنشاء التواريخ بشكل صحيح
    start_date = pd.Timestamp('2024-01-01')
    order_dates = []
    for i in range(n_rows):
        days = np.random.randint(0, 30)
        date = start_date + pd.Timedelta(days=days)
        order_dates.append(date.strftime('%Y-%m-%d'))
    
    return pd.DataFrame({
        'order_id': order_ids,
        'customer_id': customer_ids,
        'order_date': order_dates,
        'product_id': product_ids,
        'quantity': quantities,
        'price': prices,
        'total': totals
    })


@pytest.fixture
def temp_csv_file(tmp_path, sample_df):
    """Create a temporary CSV file for testing."""
    csv_path = tmp_path / "test_orders.csv"
    sample_df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return tmp_path / "test.db"


@pytest.fixture
def test_config(monkeypatch, temp_db_path):
    """Configure test environment with temporary database."""
    # إعادة تعيين config
    reset_config()
    
    monkeypatch.setenv("SQLITE_PATH", str(temp_db_path))
    monkeypatch.setenv("DB_TYPE", "sqlite")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    
    # إعادة تحميل config
    config = get_config(force_reload=True)
    
    # إنشاء قاعدة البيانات
    conn = sqlite3.connect(temp_db_path)
    conn.close()
    
    return config


@pytest.fixture
def validated_sample_df(sample_df):
    """Return validated sample DataFrame."""
    validator = OrderValidator(sample_df)
    return validator.validate()


@pytest.fixture
def transformed_sample_data(validated_sample_df):
    """Return transformed data from sample."""
    transformer = OrderTransformer(validated_sample_df)
    return transformer.transform()


@pytest.fixture
def db_connection(test_config):
    """Create a database connection for testing."""
    # إنشاء الجداول أولاً
    loader = DatabaseLoader()
    loader.create_schema()
    
    conn = sqlite3.connect(test_config.database.sqlite_path)
    yield conn
    conn.close()