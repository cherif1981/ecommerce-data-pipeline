"""Unit tests for configuration module."""

import os
import pytest
from pathlib import Path

from src.ecommerce_pipeline.config import get_config, reset_config, DatabaseConfig, Config


class TestConfig:
    """Test suite for configuration."""
    
    # ✅ إعادة تعيين config قبل كل اختبار
    @pytest.fixture(autouse=True)
    def reset_config_before_test(self):
        """Reset config before each test."""
        reset_config()
        yield
        reset_config()
    
    def test_get_config_returns_config_object(self):
        """Test that get_config returns a Config object."""
        config = get_config()
        assert isinstance(config, Config)
    
    def test_config_database_sqlite_default(self, monkeypatch):
        """Test default SQLite configuration."""
        monkeypatch.delenv('DB_TYPE', raising=False)
        monkeypatch.delenv('SQLITE_PATH', raising=False)
        
        reset_config()
        config = get_config(force_reload=True)
        assert config.database.db_type == "sqlite"
        assert "sqlite" in config.database.connection_string
    
    def test_config_database_postgresql(self, monkeypatch):
        """Test PostgreSQL configuration."""
        monkeypatch.setenv("DB_TYPE", "postgresql")
        monkeypatch.setenv("POSTGRES_HOST", "testhost")
        monkeypatch.setenv("POSTGRES_PORT", "5433")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpass")
        
        reset_config()
        config = get_config(force_reload=True)
        assert config.database.db_type == "postgresql"
        assert "postgresql://" in config.database.connection_string
        assert "testhost" in config.database.connection_string
    
    def test_config_sqlite_path(self, monkeypatch, tmp_path):
        """Test custom SQLite path."""
        custom_path = tmp_path / "custom.db"
        monkeypatch.setenv("SQLITE_PATH", str(custom_path))
        
        reset_config()
        config = get_config(force_reload=True)
        assert config.database.sqlite_path == str(custom_path)
    
    def test_config_connection_string_sqlite(self):
        """Test SQLite connection string generation."""
        db_config = DatabaseConfig(db_type="sqlite", sqlite_path="./test.db")
        assert db_config.connection_string == "sqlite:///./test.db"
    
    def test_config_connection_string_postgresql(self):
        """Test PostgreSQL connection string generation."""
        db_config = DatabaseConfig(
            db_type="postgresql",
            host="localhost",
            port=5432,
            database="testdb",
            user="testuser",
            password="testpass"
        )
        assert db_config.connection_string == "postgresql://testuser:testpass@localhost:5432/testdb"
    
    def test_config_env_variables(self, monkeypatch):
        """Test configuration from environment variables."""
        # ✅ تعيين متغيرات البيئة
        monkeypatch.setenv("PIPELINE_DATA_DIR", "/custom/data")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        reset_config()
        config = get_config(force_reload=True)
        
        # ✅ التحقق من القيم
        assert config.data_dir == "/custom/data"
        assert config.logging.level == "DEBUG"
    
    def test_config_env_variables_with_DATA_DIR(self, monkeypatch):
        """Test configuration from DATA_DIR environment variable."""
        monkeypatch.setenv("DATA_DIR", "/custom/data2")
        
        reset_config()
        config = get_config(force_reload=True)
        
        assert config.data_dir == "/custom/data2"
    
    def test_config_env_variables_priority(self, monkeypatch):
        """Test that PIPELINE_DATA_DIR takes priority over DATA_DIR."""
        monkeypatch.setenv("PIPELINE_DATA_DIR", "/priority/path")
        monkeypatch.setenv("DATA_DIR", "/fallback/path")
        
        reset_config()
        config = get_config(force_reload=True)
        
        assert config.data_dir == "/priority/path"
    
    def test_config_caching(self):
        """Test that configuration is cached."""
        config1 = get_config()
        config2 = get_config()
        
        # Should be the same object
        assert config1 is config2
    
    def test_config_reset(self):
        """Test that reset_config works."""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        
        # Should be different objects after reset
        assert config1 is not config2
    
    def test_config_logging_level_default(self):
        """Test default logging level."""
        reset_config()
        config = get_config(force_reload=True)
        assert config.logging.level == "INFO"
    
    def test_config_logging_level_from_env(self, monkeypatch):
        """Test logging level from environment."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        reset_config()
        config = get_config(force_reload=True)
        assert config.logging.level == "DEBUG"
    
    def test_config_logging_file_from_env(self, monkeypatch, tmp_path):
        """Test logging file from environment."""
        log_file = tmp_path / "test.log"
        monkeypatch.setenv("LOG_FILE", str(log_file))
        
        reset_config()
        config = get_config(force_reload=True)
        assert config.logging.file == str(log_file)
    
    def test_config_data_dir_default(self):
        """Test default data directory."""
        reset_config()
        config = get_config(force_reload=True)
        assert config.data_dir == "./data"