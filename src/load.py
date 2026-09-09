import pandas as pd
from sqlalchemy import create_engine, text
from src.config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_connection():
    """إنشاء اتصال بقاعدة البيانات (SQLite أو PostgreSQL)"""
    try:
        if DB_CONFIG.get("driver") == "sqlite":
            # استخدام SQLite
            db_path = DB_CONFIG["database"]
            engine = create_engine(f"sqlite:///{db_path}", echo=False)
            logger.info(f"✅ متصل بـ SQLite (الملف: {db_path})")
        else:
            # استخدام PostgreSQL (إذا أردت العودة له لاحقاً)
            conn_str = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            engine = create_engine(conn_str, echo=False)
            logger.info("✅ متصل بـ PostgreSQL")
        return engine
    except Exception as e:
        logger.error(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
        raise

def load_to_db(df: pd.DataFrame, table_name: str, if_exists: str = "replace"):
    """تحميل البيانات إلى قاعدة البيانات"""
    try:
        engine = create_connection()
        if df.empty:
            logger.warning("⚠️ لا يوجد بيانات للتحميل!")
            return
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        logger.info(f"✅ تم تحميل {len(df)} سجل إلى جدول {table_name}")
    except Exception as e:
        logger.error(f"❌ خطأ في التحميل: {e}")
        raise