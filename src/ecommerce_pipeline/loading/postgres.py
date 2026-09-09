"""Database loading module - supports SQLite."""

import pandas as pd
import sqlite3
from pathlib import Path

from ..config import get_config
from ..exceptions import LoadingError
from ..logging_config import get_logger

logger = get_logger(__name__)


class DatabaseLoader:
    """Load data into SQLite database."""

    def __init__(self):
        config = get_config()
        self.db_path = config.database.sqlite_path
        self.table_mapping = {
            "products": "dim_products",
            "customers": "dim_customers",
            "dates": "dim_dates",
            "order_facts": "fact_orders",
        }

    def load(self, data):
        """
        Load transformed data into SQLite database.
        
        Args:
            data: Dictionary of DataFrames to load.
            
        Raises:
            LoadingError: If loading fails.
        """
        try:
            logger.info(f"Starting load into SQLite: {self.db_path}")
            
            # Create schema first
            self.create_schema()
            
            # Connect to SQLite
            conn = sqlite3.connect(self.db_path)
            
            try:
                for key, df in data.items():
                    table_name = self.table_mapping.get(key, key)
                    self._load_table(df, table_name, conn)
                logger.info("Load completed successfully")
            finally:
                conn.close()
                
        except Exception as e:
            raise LoadingError(f"Load failed: {e}") from e

    def _load_table(self, df, table_name, conn):
        """Load a single table."""
        if df.empty:
            logger.warning(f"Empty DataFrame for {table_name}, skipping")
            return
        
        logger.info(f"Loading {len(df)} rows into {table_name}")
        
        # Load to SQLite
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit()

    def create_schema(self):
        """Create the warehouse schema if it doesn't exist."""
        # Get directory path
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to SQLite
        conn = sqlite3.connect(self.db_path)
        
        try:
            cursor = conn.cursor()
            
            # Create dim_products
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_products (
                    product_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id VARCHAR(50) UNIQUE NOT NULL,
                    product_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create dim_customers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_customers (
                    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id VARCHAR(50) UNIQUE NOT NULL,
                    customer_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create dim_dates
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_dates (
                    date_key VARCHAR(10) PRIMARY KEY,
                    order_date DATE NOT NULL,
                    year INTEGER,
                    month INTEGER,
                    day INTEGER,
                    quarter INTEGER,
                    weekday INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create fact_orders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fact_orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    customer_key INTEGER,
                    product_key INTEGER,
                    date_key VARCHAR(10),
                    quantity INTEGER,
                    price DECIMAL(10,2),
                    total DECIMAL(10,2),
                    discount DECIMAL(10,2),
                    tax DECIMAL(10,2),
                    net_amount DECIMAL(10,2),
                    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_key) REFERENCES dim_customers(customer_key),
                    FOREIGN KEY (product_key) REFERENCES dim_products(product_key),
                    FOREIGN KEY (date_key) REFERENCES dim_dates(date_key)
                )
            """)
            
            conn.commit()
            logger.info("Schema created successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Schema creation failed: {e}")
            raise
        finally:
            conn.close()