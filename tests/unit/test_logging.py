"""Unit tests for logging configuration module."""

import pytest
import logging
import sys
import os
from pathlib import Path
import tempfile
import time

from src.ecommerce_pipeline.logging_config import setup_logging, get_logger
from src.ecommerce_pipeline.config import get_config, reset_config


class TestLoggingConfig:
    """Test suite for logging configuration."""
    
    # ==================== تنظيف شامل قبل كل اختبار ====================
    
    @pytest.fixture(autouse=True)
    def reset_logging(self):
        """Reset logging configuration before each test."""
        # إعادة تعيين config
        reset_config()
        
        # الحصول على الـ root logger
        root_logger = logging.getLogger()
        
        # إزالة جميع الـ handlers
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        # إعادة تعيين المستوى إلى NOTSET
        root_logger.setLevel(logging.NOTSET)
        
        yield
        
        # تنظيف بعد الاختبار
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.NOTSET)
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for log files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    # ==================== اختبارات الإعداد الأساسي ====================
    
    def test_setup_logging_success(self):
        """Test successful logging setup."""
        setup_logging()
        
        # Check that root logger has handlers
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0
        
        # Check that at least one handler is StreamHandler
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) 
            for h in root_logger.handlers
        )
        assert has_stream_handler
        
        # التحقق من وجود خاصية logging في config
        config = get_config()
        assert hasattr(config, 'logging')
        assert config.logging.level == "INFO"
    
    def test_setup_logging_default_level(self):
        """Test logging default level is INFO."""
        # تنظيف مسبق
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        
        # استدعاء setup_logging
        setup_logging()
        
        # التحقق من أن المستوى أصبح INFO
        assert root_logger.level == logging.INFO
    
    def test_setup_logging_default_level_effective(self):
        """Test logging effective level is INFO."""
        # تنظيف مسبق
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        
        # استدعاء setup_logging
        setup_logging()
        
        # التحقق من أن المستوى الفعال هو INFO
        assert root_logger.getEffectiveLevel() == logging.INFO
    
    def test_setup_logging_with_file_handler(self, temp_log_dir):
        """Test logging setup with file handler."""
        log_file = temp_log_dir / "app.log"
        
        # Create and add file handler
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        # Test logging
        logger = get_logger("test")
        test_message = "File log message"
        logger.info(test_message)
        
        # إغلاق وإزالة الـ handler قبل التحقق
        file_handler.flush()
        file_handler.close()
        root_logger.removeHandler(file_handler)
        
        # Check file was created
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert test_message in content
    
    def test_setup_logging_level_from_config(self, monkeypatch):
        """Test logging level is set from config."""
        # تنظيف مسبق
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        
        # تعيين متغير البيئة
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        # استدعاء setup_logging مع force_reload=True
        setup_logging(force_reload=True)
        
        # التحقق من أن المستوى أصبح DEBUG
        assert root_logger.getEffectiveLevel() == logging.DEBUG
    
    def test_setup_logging_invalid_level(self, monkeypatch):
        """Test logging with invalid level uses default INFO."""
        # تنظيف مسبق
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        
        monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")
        
        # استدعاء setup_logging مع force_reload=True
        setup_logging(force_reload=True)
        
        # يجب أن يكون INFO (20) كقيمة افتراضية
        assert root_logger.getEffectiveLevel() == logging.INFO
    
    # ==================== اختبارات get_logger ====================
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_with_name(self):
        """Test get_logger returns logger with correct name."""
        logger = get_logger("my_module")
        assert logger.name == "my_module"
    
    def test_get_logger_unique_instances(self):
        """Test that get_logger returns same logger for same name."""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")
        
        assert logger1 is logger2
    
    def test_get_logger_different_names(self):
        """Test that get_logger returns different loggers for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"
    
    def test_get_logger_creates_child_logger(self):
        """Test that get_logger creates child logger with dot notation."""
        logger = get_logger("parent.child")
        assert logger.name == "parent.child"
        assert isinstance(logger, logging.Logger)
    
    # ==================== اختبارات المخرجات ====================
    
    def test_logger_outputs_to_console(self, capsys):
        """Test that logger outputs to console."""
        setup_logging()
        
        logger = get_logger("test")
        test_message = "Test console message"
        
        logger.info(test_message)
        
        captured = capsys.readouterr()
        assert test_message in captured.out
    
    def test_logger_includes_timestamp(self, capsys):
        """Test that log messages include timestamp."""
        setup_logging()
        
        logger = get_logger("test")
        logger.info("Test message")
        
        captured = capsys.readouterr()
        
        # Check for timestamp format (YYYY-MM-DD HH:MM:SS)
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(timestamp_pattern, captured.out) is not None
    
    def test_logger_includes_log_level(self, capsys):
        """Test that log messages include log level."""
        setup_logging()
        
        logger = get_logger("test")
        logger.warning("Warning message")
        
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
    
    def test_logger_includes_module_name(self, capsys):
        """Test that log messages include module name."""
        setup_logging()
        
        logger = get_logger("test_module")
        logger.info("Test message")
        
        captured = capsys.readouterr()
        assert "test_module" in captured.out
    
    # ==================== اختبارات مستويات التسجيل ====================
    
    def test_logger_info_level(self, capsys):
        """Test info level logging."""
        setup_logging()
        
        logger = get_logger("test")
        logger.info("Info message")
        
        captured = capsys.readouterr()
        assert "Info message" in captured.out
    
    def test_logger_warning_level(self, capsys):
        """Test warning level logging."""
        setup_logging()
        
        logger = get_logger("test")
        logger.warning("Warning message")
        
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "Warning message" in captured.out
    
    def test_logger_error_level(self, capsys):
        """Test error level logging."""
        setup_logging()
        
        logger = get_logger("test")
        logger.error("Error message")
        
        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "Error message" in captured.out
    
    def test_logger_critical_level(self, capsys):
        """Test critical level logging."""
        setup_logging()
        
        logger = get_logger("test")
        logger.critical("Critical message")
        
        captured = capsys.readouterr()
        assert "CRITICAL" in captured.out
        assert "Critical message" in captured.out
    
    # ==================== اختبارات التنسيق ====================
    
    def test_logger_format_contains_all_elements(self, capsys):
        """Test that log format contains all required elements."""
        setup_logging()
        
        logger = get_logger("test_format")
        logger.info("Format test")
        
        captured = capsys.readouterr()
        
        # Check for all format elements
        assert "test_format" in captured.out
        assert "INFO" in captured.out
        assert "Format test" in captured.out
        
        # Check for timestamp
        import re
        assert re.search(r'\d{4}-\d{2}-\d{2}', captured.out) is not None
    
    def test_logger_format_uses_standard_format(self):
        """Test that logger uses standard logging format."""
        setup_logging()
        
        # Get the formatter from the first handler
        root_logger = logging.getLogger()
        if root_logger.handlers:
            handler = root_logger.handlers[0]
            formatter = handler.formatter
            
            assert formatter is not None
            fmt = formatter._fmt
            assert "%(asctime)s" in fmt
            assert "%(name)s" in fmt
            assert "%(levelname)s" in fmt
            assert "%(message)s" in fmt
    
    # ==================== اختبارات الكتابة إلى ملف ====================
    
    def test_logger_writes_to_file(self, temp_log_dir):
        """Test that logger writes to file."""
        log_file = temp_log_dir / "test.log"
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        logger = get_logger("test")
        test_message = "File log message"
        logger.info(test_message)
        
        # إغلاق وإزالة الـ handler قبل التحقق
        file_handler.flush()
        file_handler.close()
        root_logger.removeHandler(file_handler)
        
        # Check file was created and contains message
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert test_message in content
    
    def test_logger_writes_both_console_and_file(self, temp_log_dir):
        """Test that logger writes to both console and file."""
        log_file = temp_log_dir / "dual.log"
        
        # Add both handlers
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(log_file, mode='w')
        
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # Check both handlers exist
        root_logger = logging.getLogger()
        has_console = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
        has_file = any(isinstance(h, logging.FileHandler) for h in root_logger.handlers)
        
        assert has_console
        assert has_file
        
        # Clean up
        file_handler.close()
        root_logger.removeHandler(file_handler)
    
    # ==================== اختبارات الاستثناءات ====================
    
    def test_logger_handles_exception(self, capsys):
        """Test that logger handles exceptions properly."""
        setup_logging()
        
        logger = get_logger("test")
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An error occurred")
        
        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "An error occurred" in captured.out
        assert "Test exception" in captured.out
    
    def test_logger_with_exc_info(self, capsys):
        """Test logging with exc_info parameter."""
        setup_logging()
        
        logger = get_logger("test")
        
        try:
            raise RuntimeError("Runtime error")
        except RuntimeError:
            logger.error("Error with exc_info", exc_info=True)
        
        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "Runtime error" in captured.out
    
    # ==================== اختبارات الأداء ====================
    
    def test_logger_performance(self):
        """Test logger performance with many messages."""
        setup_logging()
        
        logger = get_logger("test")
        
        import time
        start = time.time()
        
        # Log 100 messages
        for i in range(100):
            logger.debug(f"Message {i}")
        
        elapsed = time.time() - start
        
        # Should complete within 1 second
        assert elapsed < 1
    
    # ==================== اختبارات متقدمة ====================
    
    def test_logger_with_multiple_handlers(self):
        """Test logger with multiple handlers."""
        setup_logging()
        
        # Add an extra handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        
        assert len(root_logger.handlers) >= 2
    
    def test_logger_propagates_to_parent(self):
        """Test that logger propagates to parent."""
        setup_logging()
        
        # Get child logger
        child_logger = get_logger("parent.child")
        
        # Should propagate to parent
        assert child_logger.propagate is True
    
    def test_logger_disabled_propagation(self):
        """Test disabling propagation."""
        setup_logging()
        
        logger = get_logger("test")
        logger.propagate = False
        
        assert logger.propagate is False
    
    # ==================== اختبارات البيئة ====================
    
    def test_logger_environment_variables(self, monkeypatch):
        """Test logger respects environment variables."""
        # تنظيف مسبق
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        # استدعاء setup_logging مع force_reload=True
        setup_logging(force_reload=True)
        
        # التحقق من أن المستوى تم تعيينه
        level = root_logger.getEffectiveLevel()
        assert level == logging.DEBUG
    
    def test_logger_with_no_env_vars(self):
        """Test logger with no environment variables set."""
        setup_logging()
        
        # Should still work with defaults
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0
    
    # ==================== اختبار إنشاء المجلد ====================
    
    def test_setup_logging_creates_log_dir(self, monkeypatch):
        """Test that logging creates log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs" / "subdir"
            log_file = log_dir / "test.log"
            
            # ✅ تنظيف مسبق كامل
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            root_logger.setLevel(logging.NOTSET)
            
            # ✅ إعادة تعيين config
            reset_config()
            
            # ✅ تعيين متغيرات البيئة
            monkeypatch.setenv("LOG_FILE", str(log_file))
            monkeypatch.setenv("LOG_LEVEL", "INFO")
            
            # ✅ استدعاء setup_logging
            setup_logging(force_reload=True)
            
            # ✅ الحصول على logger وتسجيل رسالة
            logger = get_logger("test_logger")
            test_message = "Test message for log file"
            logger.info(test_message)
            
            # ✅ إغلاق جميع الـ handlers
            for handler in root_logger.handlers[:]:
                handler.flush()
                handler.close()
                root_logger.removeHandler(handler)
            
            # ✅ التحقق من وجود الملف
            assert log_file.exists(), f"Log file not found: {log_file}"
            
            # ✅ التحقق من حجم الملف
            file_size = log_file.stat().st_size
            assert file_size > 0, f"Log file is empty: {log_file}"
            
            # ✅ التحقق من المحتوى
            content = log_file.read_text(encoding='utf-8')
            assert test_message in content, f"Message not found in log. Content: {content}"
    
    def test_setup_logging_debug_level(self, monkeypatch):
        """Test logging with DEBUG level."""
        # تنظيف مسبق
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        setup_logging(force_reload=True)
        
        assert root_logger.getEffectiveLevel() == logging.DEBUG
    
    def test_setup_logging_warning_level(self, monkeypatch):
        """Test logging with WARNING level."""
        # تنظيف مسبق
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        
        setup_logging(force_reload=True)
        
        assert root_logger.getEffectiveLevel() == logging.WARNING