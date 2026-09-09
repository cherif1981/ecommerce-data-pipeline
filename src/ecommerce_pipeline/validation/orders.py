"""Order data validation module."""

import pandas as pd
import numpy as np

from ..exceptions import ValidationError
from ..logging_config import get_logger

logger = get_logger(__name__)


class OrderValidator:
    """Validate order data."""

    REQUIRED_COLUMNS = [
        "order_id",
        "customer_id",
        "order_date",
        "product_id",
        "quantity",
        "price",
        "total",
    ]

    def __init__(self, df):
        self.df = df
        self.errors = []

    def validate(self):
        """
        Validate the DataFrame and return cleaned data.
        
        Returns:
            pd.DataFrame: Validated and cleaned data.
            
        Raises:
            ValidationError: If validation fails.
        """
        self.errors = []
        
        self._check_required_columns()
        self._check_data_types()
        self._check_nulls()
        self._check_positive_values()
        self._check_date_format()
        self._check_consistent_totals()
        
        if self.errors:
            error_msg = "\n".join([f"{col}: {err}" for col, err in self.errors])
            raise ValidationError(f"Validation failed:\n{error_msg}")
        
        return self._clean_data()

    def _check_required_columns(self):
        """Check that all required columns are present."""
        missing = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
        if missing:
            self.errors.append(("required_columns", f"Missing: {missing}"))

    def _check_data_types(self):
        """Check column data types."""
        numeric_cols = ["quantity", "price", "total"]
        for col in numeric_cols:
            if col in self.df.columns:
                if not pd.api.types.is_numeric_dtype(self.df[col]):
                    # ✅ محاولة تحويل الأعمدة الرقمية
                    try:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    except Exception:
                        self.errors.append((col, f"Expected numeric, got {self.df[col].dtype}"))

    def _check_nulls(self):
        """Check for null values in required columns."""
        for col in self.REQUIRED_COLUMNS:
            if col in self.df.columns:
                null_count = self.df[col].isna().sum()
                if null_count > 0:
                    self.errors.append((col, f"Found {null_count} null values"))

    def _check_positive_values(self):
        """Check that numeric values are positive."""
        for col in ["quantity", "price", "total"]:
            if col in self.df.columns:
                try:
                    negative = (self.df[col] <= 0).sum()
                    if negative > 0:
                        self.errors.append((col, f"Found {negative} non-positive values"))
                except Exception:
                    pass

    def _check_date_format(self):
        """Check that order_date is in valid format."""
        if "order_date" in self.df.columns:
            try:
                pd.to_datetime(self.df["order_date"])
            except Exception:
                self.errors.append(("order_date", "Invalid date format"))

    def _check_consistent_totals(self):
        """Check that total = quantity * price."""
        if all(col in self.df.columns for col in ["quantity", "price", "total"]):
            try:
                # ✅ التحقق من أن total = quantity * price
                calculated = self.df["quantity"] * self.df["price"]
                # ✅ استخدام np.isclose للتعامل مع أخطاء التقريب
                mismatch = (~np.isclose(self.df["total"], calculated, rtol=1e-5, atol=0.01)).sum()
                if mismatch > 0:
                    # ✅ إصلاح البيانات بدلاً من رفع خطأ
                    logger.warning(f"Found {mismatch} rows with inconsistent totals, fixing...")
                    self.df["total"] = calculated
            except Exception as e:
                self.errors.append(("total", f"Cannot check consistency: {e}"))

    def _clean_data(self):
        """Clean and prepare validated data."""
        df = self.df.copy()
        
        try:
            df["order_date"] = pd.to_datetime(df["order_date"])
        except Exception:
            pass
        
        for col in ["quantity", "price", "total"]:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception:
                pass
        
        # ✅ إزالة التكرارات
        if "order_id" in df.columns:
            df = df.drop_duplicates(subset=["order_id"])
        
        logger.info(f"Validated {len(df)} rows after cleaning")
        return df