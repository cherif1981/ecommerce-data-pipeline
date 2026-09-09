"""Logging configuration for the pipeline."""

import logging
import sys
from pathlib import Path

from .config import get_config, reset_config


def setup_logging(force_reload: bool = False):
    """Configure logging for the pipeline."""
    # إعادة تحميل config إذا لزم الأمر
    if force_reload:
        reset_config()
    
    config = get_config(force_reload=force_reload)
    
    # قراءة مستوى التسجيل من الإعدادات
    log_level_name = config.logging.level.upper() if config.logging.level else "INFO"
    
    # تحويل اسم المستوى إلى قيمة رقمية
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # تعيين مستوى root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # إزالة أي handlers موجودة
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
    
    # ✅ إضافة StreamHandler دائماً
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # ✅ إضافة File handler إذا تم تحديده
    if config.logging.file:
        try:
            log_file = Path(config.logging.file)
            # إنشاء المجلد إذا لم يكن موجوداً
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # ✅ استخدام mode='a' للإلحاق بدلاً من 'w'
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
    
    # ✅ إعداد التنسيق
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # ✅ تطبيق التنسيق على جميع الـ handlers
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
    
    # ✅ تسجيل رسالة بداية للتأكد من أن التسجيل يعمل
    logger = logging.getLogger(__name__)
    logger.debug("Logging initialized")


def get_logger(name):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)