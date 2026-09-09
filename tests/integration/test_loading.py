"""Integration tests for loading module - Fixed."""

import pytest
import pandas as pd
import sqlite3
from pathlib import Path

from src.ecommerce_pipeline.loading.postgres import DatabaseLoader
from src.ecommerce_pipeline.validation.orders import OrderValidator
from src.ecommerce_pipeline.transformation.orders import OrderTransformer


class TestDatabaseLoader:
    """Integration test suite for DatabaseLoader."""

    def test_load_simple(self, sample_df, test_config):
        """Simple test: load sample data and verify."""
        
        # ✅ 1. إعداد البيانات
        df = sample_df.copy()
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # إنشاء الأبعاد
        products = df[['product_id']].drop_duplicates()
        products['product_name'] = 'Product_' + products['product_id'].astype(str)
        
        customers = df[['customer_id']].drop_duplicates()
        customers['customer_name'] = 'Customer_' + customers['customer_id'].astype(str)
        
        dates = df[['order_date']].drop_duplicates()
        dates['date_key'] = dates['order_date'].astype(str)
        dates['year'] = dates['order_date'].dt.year
        dates['month'] = dates['order_date'].dt.month
        dates['day'] = dates['order_date'].dt.day
        
        facts = df.copy()
        facts['date_key'] = facts['order_date'].astype(str)
        facts['product_key'] = facts['product_id'].map(
            dict(zip(products['product_id'], products.index))
        )
        facts['customer_key'] = facts['customer_id'].map(
            dict(zip(customers['customer_id'], customers.index))
        )
        
        data = {
            'products': products,
            'customers': customers,
            'dates': dates,
            'order_facts': facts
        }
        
        # ✅ 2. التحميل
        loader = DatabaseLoader()
        loader.load(data)
        
        # ✅ 3. التحقق المباشر من قاعدة البيانات
        db_path = test_config.database.sqlite_path
        assert Path(db_path).exists()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # عرض جميع الجداول
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n📋 Tables: {tables}")
        
        # التحقق من وجود الجداول
        assert 'dim_products' in tables
        assert 'dim_customers' in tables
        assert 'dim_dates' in tables
        assert 'fact_orders' in tables
        
        # التحقق من البيانات
        cursor.execute("SELECT COUNT(*) FROM fact_orders")
        count = cursor.fetchone()[0]
        print(f"✅ fact_orders: {count} rows")
        assert count == len(df)
        
        conn.close()
        print("✅ All tests passed!")

    def test_load_with_validation(self, sample_df, test_config):
        """Test loading with full validation and transformation."""
        
        # ✅ 1. التحقق والتحويل
        validator = OrderValidator(sample_df)
        validated_df = validator.validate()
        
        transformer = OrderTransformer(validated_df)
        data = transformer.transform()
        
        # ✅ 2. التحميل
        loader = DatabaseLoader()
        loader.load(data)
        
        # ✅ 3. التحقق
        db_path = test_config.database.sqlite_path
        assert Path(db_path).exists()
        
        conn = sqlite3.connect(db_path)
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM fact_orders")
            count = cursor.fetchone()[0]
            assert count > 0
            print(f"✅ Loaded {count} orders")
        finally:
            conn.close()

    def test_schema_creation(self, test_config):
        """Test schema creation."""
        loader = DatabaseLoader()
        loader.create_schema()
        
        db_path = test_config.database.sqlite_path
        assert Path(db_path).exists()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'dim_products' in tables
        assert 'dim_customers' in tables
        assert 'dim_dates' in tables
        assert 'fact_orders' in tables
        print("✅ Schema created successfully")
        
        conn.close()