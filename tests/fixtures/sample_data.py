"""Sample data fixtures for tests."""

import pandas as pd
from pathlib import Path


def get_sample_orders():
    """Return sample order data."""
    return pd.DataFrame({
        'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
        'customer_id': ['CUST001', 'CUST002', 'CUST001', 'CUST003', 'CUST002'],
        'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
        'product_id': ['PROD001', 'PROD002', 'PROD003', 'PROD001', 'PROD004'],
        'quantity': [2, 1, 3, 1, 2],
        'price': [50.00, 75.00, 30.00, 50.00, 40.00],
        'total': [100.00, 75.00, 90.00, 50.00, 80.00]
    })


def get_sample_with_errors():
    """Return sample data with errors for testing validation."""
    return pd.DataFrame({
        'order_id': ['ORD001', 'ORD002', None, 'ORD004', 'ORD005'],
        'customer_id': ['CUST001', None, 'CUST001', 'CUST003', 'CUST002'],
        'order_date': ['2024-01-15', 'invalid', '2024-01-17', '2024-01-18', '2024-01-19'],
        'product_id': ['PROD001', 'PROD002', 'PROD003', 'PROD001', 'PROD004'],
        'quantity': [2, 1, -3, 1, 2],
        'price': [50.00, -75.00, 30.00, 50.00, 40.00],
        'total': [100.00, 75.00, 90.00, 50.00, 999.99]
    })