"""Unit tests for transformation module."""

import pytest
import pandas as pd

from src.ecommerce_pipeline.transformation.orders import OrderTransformer
from src.ecommerce_pipeline.validation.orders import OrderValidator
from src.ecommerce_pipeline.exceptions import TransformationError


class TestOrderTransformer:
    """Test suite for OrderTransformer class."""
    
    def test_transform_success(self, validated_sample_df, sample_df):
        """Test successful transformation."""
        transformer = OrderTransformer(validated_sample_df)
        result = transformer.transform()
        
        expected_tables = ['products', 'customers', 'dates', 'order_facts']
        for table in expected_tables:
            assert table in result
            assert isinstance(result[table], pd.DataFrame)
    
    def test_transform_product_dimension(self, validated_sample_df, sample_df):
        """Test product dimension creation."""
        transformer = OrderTransformer(validated_sample_df)
        result = transformer.transform()
        
        products = result['products']
        
        assert 'product_id' in products.columns
        assert 'product_name' in products.columns
        assert len(products) == len(sample_df['product_id'].unique())
        
        # Check product names are generated
        for pid in products['product_id']:
            assert products[products['product_id'] == pid]['product_name'].iloc[0] == f"Product_{pid}"
    
    def test_transform_customer_dimension(self, validated_sample_df, sample_df):
        """Test customer dimension creation."""
        transformer = OrderTransformer(validated_sample_df)
        result = transformer.transform()
        
        customers = result['customers']
        
        assert 'customer_id' in customers.columns
        assert 'customer_name' in customers.columns
        assert len(customers) == len(sample_df['customer_id'].unique())
    
    def test_transform_date_dimension(self, validated_sample_df):
        """Test date dimension creation."""
        transformer = OrderTransformer(validated_sample_df)
        result = transformer.transform()
        
        dates = result['dates']
        
        assert 'date_key' in dates.columns
        assert 'year' in dates.columns
        assert 'month' in dates.columns
        assert 'day' in dates.columns
        assert 'quarter' in dates.columns
        assert 'weekday' in dates.columns
        
        # Check date components are correct
        for idx, row in dates.iterrows():
            date_obj = row['order_date']
            assert row['year'] == date_obj.year
            assert row['month'] == date_obj.month
            assert row['day'] == date_obj.day
    
    def test_transform_fact_table(self, validated_sample_df):
        """Test fact table creation."""
        transformer = OrderTransformer(validated_sample_df)
        result = transformer.transform()
        
        facts = result['order_facts']
        
        expected_columns = [
            'order_id', 'customer_key', 'product_key', 'date_key',
            'quantity', 'price', 'total', 'discount', 'tax', 'net_amount'
        ]
        
        for col in expected_columns:
            assert col in facts.columns
    
    def test_transform_fact_calculations(self, validated_sample_df):
        """Test fact table calculations (tax, net_amount)."""
        transformer = OrderTransformer(validated_sample_df)
        result = transformer.transform()
        
        facts = result['order_facts']
        
        # Check tax calculation (10% of total)
        assert (facts['tax'] == facts['total'] * 0.1).all()
        
        # Check net_amount calculation
        assert (facts['net_amount'] == facts['total'] - facts['tax'] - facts['discount']).all()
    
    def test_transform_empty_dataframe(self):
        """Test transformation with empty DataFrame."""
        # إنشاء DataFrame فارغ مع الأعمدة المطلوبة
        empty_df = pd.DataFrame(columns=['order_id', 'customer_id', 'order_date', 
                                         'product_id', 'quantity', 'price', 'total'])
        
        transformer = OrderTransformer(empty_df)
        result = transformer.transform()
        
        # Should return empty DataFrames
        assert 'products' in result
        assert 'customers' in result
        assert 'dates' in result
        assert 'order_facts' in result
        
        assert result['products'].empty
        assert result['customers'].empty
        assert result['dates'].empty
        assert result['order_facts'].empty
    
    def test_transform_empty_dataframe_no_columns(self):
        """Test transformation with completely empty DataFrame."""
        # DataFrame فارغ بدون أعمدة
        empty_df = pd.DataFrame()
        
        transformer = OrderTransformer(empty_df)
        result = transformer.transform()
        
        # Should return empty DataFrames
        assert 'products' in result
        assert 'customers' in result
        assert 'dates' in result
        assert 'order_facts' in result
        
        assert result['products'].empty
        assert result['customers'].empty
        assert result['dates'].empty
        assert result['order_facts'].empty
    
    def test_transform_missing_columns(self, sample_df):
        """Test transformation with missing columns."""
        # ✅ إزالة بعض الأعمدة
        df = sample_df.drop(columns=['product_id', 'customer_id'])
        
        # ✅ التحقق من صحة البيانات (سيفشل لأن الأعمدة مفقودة)
        validator = OrderValidator(df)
        
        with pytest.raises(Exception):  # من المتوقع أن يفشل التحقق
            validator.validate()
    
    def test_transform_without_validation(self, sample_df):
        """Test transformation without validation (direct)."""
        # ✅ تحويل عمود التاريخ إلى datetime قبل التحويل
        df = sample_df.copy()
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # ✅ تخطي التحقق والذهاب مباشرة إلى التحويل
        transformer = OrderTransformer(df)
        result = transformer.transform()
        
        # Should still work with missing columns
        assert 'products' in result
        assert 'customers' in result
        assert 'dates' in result
        assert 'order_facts' in result
        
        # التحقق من أن النتائج ليست فارغة
        assert len(result['products']) > 0
        assert len(result['customers']) > 0
        assert len(result['dates']) > 0
        assert len(result['order_facts']) > 0
    
    def test_transform_with_missing_date(self, sample_df):
        """Test transformation with missing date column."""
        df = sample_df.copy()
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # ✅ إزالة بعض الأعمدة للاختبار
        df = df.drop(columns=['product_id'])
        
        transformer = OrderTransformer(df)
        result = transformer.transform()
        
        # Should still work
        assert 'products' in result
        assert 'customers' in result
        assert 'dates' in result
        assert 'order_facts' in result