"""Order data transformation module."""

import pandas as pd
from typing import Dict

from ..exceptions import TransformationError
from ..logging_config import get_logger

logger = get_logger(__name__)


class OrderTransformer:
    """Transform order data for warehouse loading."""

    def __init__(self, df):
        self.df = df

    def transform(self):
        """
        Transform order data into dimensional model.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of fact and dimension tables.
            
        Raises:
            TransformationError: If transformation fails.
        """
        try:
            logger.info("Starting transformation...")
            
            # ✅ التحقق من DataFrame الفارغ
            if self.df.empty:
                logger.warning("Empty DataFrame provided, returning empty tables")
                return {
                    "products": pd.DataFrame(),
                    "customers": pd.DataFrame(),
                    "dates": pd.DataFrame(),
                    "order_facts": pd.DataFrame()
                }
            
            # ✅ التأكد من أن order_date هو datetime
            if 'order_date' in self.df.columns:
                try:
                    self.df['order_date'] = pd.to_datetime(self.df['order_date'])
                except Exception as e:
                    logger.warning(f"Could not convert order_date to datetime: {e}")
            
            # Create dimension tables
            products = self._create_product_dimension()
            customers = self._create_customer_dimension()
            dates = self._create_date_dimension()
            
            # Create fact table
            order_facts = self._create_order_facts(products, customers, dates)
            
            logger.info(
                f"Transformation complete: "
                f"{len(products)} products, "
                f"{len(customers)} customers, "
                f"{len(order_facts)} order facts"
            )
            
            return {
                "products": products,
                "customers": customers,
                "dates": dates,
                "order_facts": order_facts,
            }
        except Exception as e:
            raise TransformationError(f"Transformation failed: {e}") from e

    def _create_product_dimension(self):
        """Create product dimension table."""
        # ✅ التحقق من وجود العمود
        if 'product_id' not in self.df.columns:
            return pd.DataFrame()
        
        products = self.df[["product_id"]].drop_duplicates().copy()
        products["product_name"] = "Product_" + products["product_id"].astype(str)
        return products

    def _create_customer_dimension(self):
        """Create customer dimension table."""
        # ✅ التحقق من وجود العمود
        if 'customer_id' not in self.df.columns:
            return pd.DataFrame()
        
        customers = self.df[["customer_id"]].drop_duplicates().copy()
        customers["customer_name"] = "Customer_" + customers["customer_id"].astype(str)
        return customers

    def _create_date_dimension(self):
        """Create date dimension table."""
        # ✅ التحقق من وجود العمود
        if 'order_date' not in self.df.columns:
            return pd.DataFrame()
        
        dates = self.df[["order_date"]].drop_duplicates().copy()
        
        # ✅ التأكد من أن order_date هو datetime
        if not pd.api.types.is_datetime64_any_dtype(dates['order_date']):
            try:
                dates['order_date'] = pd.to_datetime(dates['order_date'])
            except Exception:
                return pd.DataFrame()
        
        dates["year"] = dates["order_date"].dt.year
        dates["month"] = dates["order_date"].dt.month
        dates["day"] = dates["order_date"].dt.day
        dates["quarter"] = dates["order_date"].dt.quarter
        dates["weekday"] = dates["order_date"].dt.weekday
        dates["date_key"] = dates["order_date"].astype(str)
        return dates

    def _create_order_facts(self, products, customers, dates):
        """Create order fact table."""
        facts = self.df.copy()
        
        # ✅ التأكد من أن order_date هو datetime
        if 'order_date' in facts.columns and not pd.api.types.is_datetime64_any_dtype(facts['order_date']):
            try:
                facts['order_date'] = pd.to_datetime(facts['order_date'])
            except Exception:
                pass
        
        # Add surrogate keys
        if not products.empty and 'product_id' in facts.columns:
            facts["product_key"] = facts["product_id"].map(
                dict(zip(products["product_id"], products.index))
            )
        else:
            facts["product_key"] = None
        
        if not customers.empty and 'customer_id' in facts.columns:
            facts["customer_key"] = facts["customer_id"].map(
                dict(zip(customers["customer_id"], customers.index))
            )
        else:
            facts["customer_key"] = None
        
        if not dates.empty and 'order_date' in facts.columns:
            facts["date_key"] = facts["order_date"].astype(str)
        else:
            facts["date_key"] = None
        
        # Calculate derived metrics
        facts["discount"] = 0.0
        if 'total' in facts.columns:
            facts["tax"] = facts["total"] * 0.1
            facts["net_amount"] = facts["total"] - facts["tax"] - facts["discount"]
        else:
            facts["tax"] = 0.0
            facts["net_amount"] = 0.0
        
        # ✅ اختيار الأعمدة الموجودة فقط
        columns = ['order_id', 'customer_key', 'product_key', 'date_key', 
                   'quantity', 'price', 'total', 'discount', 'tax', 'net_amount']
        
        # ✅ استخدام الأعمدة الموجودة فقط
        available_columns = [col for col in columns if col in facts.columns]
        
        return facts[available_columns]