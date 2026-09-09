"""Unit tests for validation module."""

import pytest
import pandas as pd

from src.ecommerce_pipeline.validation.orders import OrderValidator
from src.ecommerce_pipeline.exceptions import ValidationError


class TestOrderValidator:
    """Test suite for OrderValidator class."""
    
    def test_validate_success(self, sample_df):
        """Test successful validation."""
        validator = OrderValidator(sample_df)
        validated_df = validator.validate()
        
        assert isinstance(validated_df, pd.DataFrame)
        assert len(validated_df) == len(sample_df)
    
    def test_validate_required_columns_present(self, sample_df):
        """Test that all required columns are present."""
        validator = OrderValidator(sample_df)
        validated_df = validator.validate()
        
        for col in validator.REQUIRED_COLUMNS:
            assert col in validated_df.columns
    
    def test_validate_missing_columns(self, sample_df):
        """Test validation with missing columns."""
        df = sample_df.drop(columns=['total'])
        validator = OrderValidator(df)
        
        with pytest.raises(ValidationError) as excinfo:
            validator.validate()
        
        assert "Missing" in str(excinfo.value)
    
    def test_validate_negative_quantity(self, sample_df):
        """Test validation with negative quantity."""
        df = sample_df.copy()
        df.loc[0, 'quantity'] = -1
        
        validator = OrderValidator(df)
        
        with pytest.raises(ValidationError) as excinfo:
            validator.validate()
        
        assert "non-positive" in str(excinfo.value)
    
    def test_validate_negative_price(self, sample_df):
        """Test validation with negative price."""
        df = sample_df.copy()
        df.loc[0, 'price'] = -50.00
        
        validator = OrderValidator(df)
        
        with pytest.raises(ValidationError) as excinfo:
            validator.validate()
        
        assert "non-positive" in str(excinfo.value)
    
    def test_validate_inconsistent_totals(self, sample_df):
        """Test validation with inconsistent totals."""
        df = sample_df.copy()
        df.loc[0, 'total'] = 999.99
        
        validator = OrderValidator(df)
        
        with pytest.raises(ValidationError) as excinfo:
            validator.validate()
        
        assert "inconsistent totals" in str(excinfo.value)
    
    def test_validate_null_values(self, sample_df):
        """Test validation with null values."""
        df = sample_df.copy()
        df.loc[0, 'price'] = None
        
        validator = OrderValidator(df)
        
        with pytest.raises(ValidationError) as excinfo:
            validator.validate()
        
        assert "null values" in str(excinfo.value)
    
    def test_validate_duplicates_removed(self, sample_df):
        """Test validation removes duplicates."""
        df = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
        validator = OrderValidator(df)
        validated_df = validator.validate()
        
        assert len(validated_df) == len(sample_df)
    
    def test_validate_date_format_invalid(self, sample_df):
        """Test validation with invalid date format."""
        df = sample_df.copy()
        df.loc[0, 'order_date'] = 'invalid-date'
        
        validator = OrderValidator(df)
        
        with pytest.raises(ValidationError) as excinfo:
            validator.validate()
        
        assert "Invalid date format" in str(excinfo.value)
    
    def test_validate_data_types_correct(self, sample_df):
        """Test that validation converts types correctly."""
        validator = OrderValidator(sample_df)
        validated_df = validator.validate()
        
        # Check types after validation
        assert pd.api.types.is_datetime64_any_dtype(validated_df['order_date'])
        assert pd.api.types.is_numeric_dtype(validated_df['quantity'])
        assert pd.api.types.is_numeric_dtype(validated_df['price'])
        assert pd.api.types.is_numeric_dtype(validated_df['total'])
    
    def test_validate_handles_empty_dataframe(self):
        """Test validation with empty DataFrame."""
        empty_df = pd.DataFrame(columns=OrderValidator.REQUIRED_COLUMNS)
        validator = OrderValidator(empty_df)
        
        with pytest.raises(ValidationError):
            validator.validate()
    
    def test_validate_handles_extra_columns(self, sample_df):
        """Test validation with extra columns."""
        df = sample_df.copy()
        df['extra_column'] = 'extra_value'
        
        validator = OrderValidator(df)
        validated_df = validator.validate()
        
        # Extra column should be preserved
        assert 'extra_column' in validated_df.columns
    
    def test_validate_with_special_characters(self, sample_df):
        """Test validation with special characters."""
        df = sample_df.copy()
        df.loc[0, 'customer_id'] = 'CUST-001_SPECIAL'
        
        validator = OrderValidator(df)
        validated_df = validator.validate()
        
        assert validated_df['customer_id'][0] == 'CUST-001_SPECIAL'
    
    def test_validate_with_very_large_numbers(self, sample_df):
        """Test validation with very large numbers."""
        df = sample_df.copy()
        df.loc[0, 'quantity'] = 99999
        df.loc[0, 'total'] = 99999 * df.loc[0, 'price']
        
        validator = OrderValidator(df)
        validated_df = validator.validate()
        
        assert validated_df['quantity'][0] == 99999
    
    def test_validate_with_decimal_quantities(self, sample_df):
        """Test validation with decimal quantities."""
        df = sample_df.copy()
        df.loc[0, 'quantity'] = 2.5
        
        validator = OrderValidator(df)
        validated_df = validator.validate()
        
        # Should convert to numeric
        assert isinstance(validated_df['quantity'][0], (int, float))