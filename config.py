"""Configuration management for the ETL pipeline."""

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig(BaseModel):
    """Database configuration."""
    
    db_type: str = Field(default="sqlite")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(default="ecommerce")
    user: str = Field(default="etl_user")
    password: str = Field(default="secure_password")
    sqlite_path: str = Field(default="./ecommerce.db")

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class Config(BaseModel):
    """Master configuration for the pipeline."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    data_dir: str = Field(default="./data")

    class Config:
        env_prefix = "PIPELINE_"


# ✅ بدون lru_cache - استخدام متغير عام بسيط
_config_instance = None

def get_config():
    """Load configuration from environment variables."""
    global _config_instance
    
    if _config_instance is None:
        db_type = os.getenv("DB_TYPE", "sqlite")
        
        _config_instance = Config(
            database=DatabaseConfig(
                db_type=db_type,
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                database=os.getenv("POSTGRES_DB", "ecommerce"),
                user=os.getenv("POSTGRES_USER", "etl_user"),
                password=os.getenv("POSTGRES_PASSWORD", "secure_password"),
                sqlite_path=os.getenv("SQLITE_PATH", "./ecommerce.db"),
            ),
            data_dir=os.getenv("DATA_DIR", "./data"),
        )
    
    return _config_instance