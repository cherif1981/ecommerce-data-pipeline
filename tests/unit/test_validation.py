import pandas as pd
import pytest

from src.ecommerce_pipeline.exceptions import ValidationError
from src.ecommerce_pipeline.validation.orders import OrderValidator


def valid_orders():
    return pd.DataFrame(
        {
            "order_id": ["ORD001", "ORD002"],
            "customer_id": ["CUST001", "CUST002"],
            "order_date": ["2024-01-01", "2024-01-02"],
            "product_id": ["PROD001", "PROD002"],
            "quantity": [2, 1],
            "price": [50.0, 75.0],
            "total": [100.0, 75.0],
        }
    )


class TestOrderValidator:
    def test_valid_data_passes(self):
        df = valid_orders()

        result = OrderValidator(df).validate()

        assert len(result) == 2
        assert isinstance(result, pd.DataFrame)

    def test_required_columns_are_enforced(self):
        df = valid_orders().drop(columns=["customer_id"])

        with pytest.raises(ValidationError, match="required_columns"):
            OrderValidator(df).validate()

    def test_null_values_are_rejected(self):
        df = valid_orders()
        df.loc[0, "customer_id"] = None

        with pytest.raises(ValidationError, match="customer_id"):
            OrderValidator(df).validate()

    @pytest.mark.parametrize(
        "column,value",
        [
            ("quantity", 0),
            ("quantity", -1),
            ("price", 0),
            ("price", -10),
            ("total", 0),
            ("total", -5),
        ],
    )
    def test_non_positive_values_are_rejected(self, column, value):
        df = valid_orders()
        df.loc[0, column] = value

        with pytest.raises(ValidationError, match=column):
            OrderValidator(df).validate()

    def test_invalid_date_is_rejected(self):
        df = valid_orders()
        df.loc[0, "order_date"] = "not-a-date"

        with pytest.raises(ValidationError, match="order_date"):
            OrderValidator(df).validate()

    def test_numeric_strings_are_converted(self):
        df = valid_orders()

        df["quantity"] = df["quantity"].astype(str)
        df["price"] = df["price"].astype(str)
        df["total"] = df["total"].astype(str)

        result = OrderValidator(df).validate()

        assert pd.api.types.is_numeric_dtype(result["quantity"])
        assert pd.api.types.is_numeric_dtype(result["price"])
        assert pd.api.types.is_numeric_dtype(result["total"])

    def test_inconsistent_total_is_corrected(self):
        df = valid_orders()

        df.loc[0, "quantity"] = 3
        df.loc[0, "price"] = 20
        df.loc[0, "total"] = 999

        result = OrderValidator(df).validate()

        assert result.loc[0, "total"] == 60

    def test_duplicate_order_ids_are_removed(self):
        df = pd.concat([valid_orders(), valid_orders().iloc[[0]]])

        result = OrderValidator(df).validate()

        assert len(result) == 2
        assert result["order_id"].is_unique

    def test_order_date_is_converted_to_datetime(self):
        result = OrderValidator(valid_orders()).validate()

        assert pd.api.types.is_datetime64_any_dtype(result["order_date"])

    def test_original_dataframe_is_not_modified_by_cleaning(self):
        df = valid_orders()

        result = OrderValidator(df).validate()

        assert result is not df