"""Configuration management for the ETL pipeline."""

import os
from typing import Optional
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


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: str = Field(default="INFO")
    file: Optional[str] = Field(default=None)


class Config(BaseModel):
    """Master configuration for the pipeline."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    data_dir: str = Field(default="./data")

    class Config:
        env_prefix = "PIPELINE_"


# ✅ استخدام متغير عام مع إمكانية إعادة التعيين للاختبارات
_config_instance = None
_force_reload = False

def get_config(force_reload: bool = False):
    """Load configuration from environment variables."""
    global _config_instance, _force_reload
    
    if _config_instance is None or force_reload or _force_reload:
        db_type = os.getenv("DB_TYPE", "sqlite")
        
        # ✅ قراءة data_dir من متغيرات البيئة
        data_dir = os.getenv("PIPELINE_DATA_DIR", os.getenv("DATA_DIR", "./data"))
        
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
            logging=LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                file=os.getenv("LOG_FILE", None),
            ),
            data_dir=data_dir,
        )
        _force_reload = False
    
    return _config_instance


def reset_config():
    """Reset configuration cache (useful for testing)."""
    global _config_instance, _force_reload
    _config_instance = None
    _force_reload = True