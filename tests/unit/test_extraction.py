import pandas as pd
import pytest

from src.ecommerce_pipeline.exceptions import ExtractionError
from src.ecommerce_pipeline.extraction.csv import CSVExtractor


class TestCSVExtractor:
    def test_extract_valid_csv(self, tmp_path):
        csv_file = tmp_path / "orders.csv"

        csv_file.write_text(
            "order_id,customer_id,order_date,product_id,quantity,price,total\n"
            "ORD001,CUST001,2024-01-01,PROD001,2,50,100\n"
            "ORD002,CUST002,2024-01-02,PROD002,1,75,75\n"
        )

        result = CSVExtractor(csv_file).extract()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == [
            "order_id",
            "customer_id",
            "order_date",
            "product_id",
            "quantity",
            "price",
            "total",
        ]

    def test_extract_preserves_values(self, tmp_path):
        csv_file = tmp_path / "orders.csv"

        csv_file.write_text(
            "order_id,customer_id,order_date,product_id,quantity,price,total\n"
            "ORD001,CUST001,2024-01-01,PROD001,2,50.5,101\n"
        )

        result = CSVExtractor(csv_file).extract()

        assert result.loc[0, "order_id"] == "ORD001"
        assert result.loc[0, "quantity"] == 2
        assert result.loc[0, "price"] == 50.5
        assert result.loc[0, "total"] == 101

    def test_extract_missing_file(self, tmp_path):
        missing_file = tmp_path / "missing.csv"

        with pytest.raises(ExtractionError, match="File not found"):
            CSVExtractor(missing_file).extract()

    def test_extract_empty_file_raises_error(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises(ExtractionError):
            CSVExtractor(csv_file).extract()

    def test_extract_header_only(self, tmp_path):
        csv_file = tmp_path / "orders.csv"

        csv_file.write_text(
            "order_id,customer_id,order_date,product_id,quantity,price,total\n"
        )

        result = CSVExtractor(csv_file).extract()

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert len(result.columns) == 7

    def test_extract_unicode(self, tmp_path):
        csv_file = tmp_path / "orders.csv"

        csv_file.write_text(
            "order_id,customer_id,order_date,product_id,quantity,price,total\n"
            "ORD001,عميل001,2024-01-01,منتج001,2,50,100\n",
            encoding="utf-8",
        )

        result = CSVExtractor(csv_file).extract()

        assert result.loc[0, "customer_id"] == "عميل001"
        assert result.loc[0, "product_id"] == "منتج001"

    def test_extract_extra_columns_are_preserved(self, tmp_path):
        csv_file = tmp_path / "orders.csv"

        csv_file.write_text(
            "order_id,customer_id,order_date,product_id,quantity,price,total,status\n"
            "ORD001,CUST001,2024-01-01,PROD001,2,50,100,paid\n"
        )

        result = CSVExtractor(csv_file).extract()

        assert "status" in result.columns
        assert result.loc[0, "status"] == "paid"