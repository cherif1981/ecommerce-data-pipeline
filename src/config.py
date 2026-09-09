import os
from dotenv import load_dotenv

load_dotenv()

# تكوين قاعدة البيانات لاستخدام SQLite
DB_CONFIG = {
    "driver": "sqlite",
    "database": "ecommerce.db"  # سيتم إنشاء هذا الملف في مجلد المشروع
}