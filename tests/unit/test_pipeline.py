"""Unit tests for pipeline module."""

import pytest
from pathlib import Path
import sys

from src.ecommerce_pipeline.pipeline import ETLPipeline, main, cli_command
from src.ecommerce_pipeline.exceptions import PipelineError


class TestETLPipeline:
    """Test suite for ETLPipeline class."""
    
    def test_pipeline_init(self, temp_csv_file):
        """Test pipeline initialization."""
        pipeline = ETLPipeline(temp_csv_file)
        assert pipeline.source_file == temp_csv_file
        assert pipeline.extractor is not None
        assert pipeline.loader is not None
    
    def test_pipeline_run_success(self, temp_csv_file, test_config):
        """Test successful pipeline run."""
        pipeline = ETLPipeline(temp_csv_file)
        pipeline.run()
        
        # Verify database was created
        assert Path(test_config.database.sqlite_path).exists()
    
    def test_pipeline_run_with_schema_creation(self, temp_csv_file, test_config):
        """Test pipeline run with schema creation."""
        pipeline = ETLPipeline(temp_csv_file)
        pipeline.run()
        
        # Verify tables exist
        import sqlite3
        conn = sqlite3.connect(test_config.database.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'dim_products' in tables
        assert 'dim_customers' in tables
        assert 'dim_dates' in tables
        assert 'fact_orders' in tables
        conn.close()
    
    def test_pipeline_file_not_found(self):
        """Test pipeline with missing file."""
        pipeline = ETLPipeline("nonexistent.csv")
        
        with pytest.raises(PipelineError):
            pipeline.run()
    
    def test_pipeline_main_function(self, temp_csv_file, monkeypatch):
        """Test main function."""
        # منع SystemExit
        def mock_exit(code=0):
            raise SystemExit(code)
        
        monkeypatch.setattr(sys, 'exit', mock_exit)
        
        # Mock sys.argv
        monkeypatch.setattr(sys, 'argv', ['pipeline.py', str(temp_csv_file)])
        
        # Should not raise exception
        try:
            main()
        except SystemExit as e:
            # إذا كان الخروج بسبب نجاح (code 0) فهذا مقبول
            assert e.code == 0
    
    def test_pipeline_main_no_args(self, monkeypatch, capsys):
        """Test main function with no arguments."""
        # منع SystemExit
        def mock_exit(code=0):
            raise SystemExit(code)
        
        monkeypatch.setattr(sys, 'exit', mock_exit)
        
        # Mock sys.argv with no args
        monkeypatch.setattr(sys, 'argv', ['pipeline.py'])
        
        try:
            main()
        except SystemExit as e:
            # الخروج مع code 0 عند عرض المساعدة
            assert e.code == 0
        
        # التحقق من عرض المساعدة
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
    
    def test_pipeline_cli_command(self, temp_csv_file, monkeypatch, test_config):
        """Test cli_command function."""
        # Mock sys.argv
        monkeypatch.setattr(sys, 'argv', ['pipeline.py', str(temp_csv_file)])
        
        # استدعاء cli_command مباشرة
        cli_command(str(temp_csv_file))
        
        # Verify database was created
        assert Path(test_config.database.sqlite_path).exists()
    
    def test_pipeline_cli_command_file_not_found(self):
        """Test cli_command with missing file."""
        with pytest.raises(PipelineError):
            cli_command("nonexistent.csv")
    
    def test_pipeline_run_with_exception(self, monkeypatch, tmp_path):
        """Test pipeline run with exception."""
        # إنشاء ملف CSV فارغ
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("")
        
        pipeline = ETLPipeline(csv_path)
        
        with pytest.raises(PipelineError):
            pipeline.run()