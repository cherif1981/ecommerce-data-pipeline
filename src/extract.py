import pandas as pd
import os
import requests
from pathlib import Path

def create_default_data() -> pd.DataFrame:
    """
    إنشاء بيانات افتراضية للاختبار (تُستخدم عندما يكون الملف فارغاً أو غير موجود)
    """
    print("📊 إنشاء بيانات تجريبية للاختبار...")
    
    data = {
        'order_id': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'customer_id': [1, 1, 2, 3, 2, 4, 3, 5, 4, 6],
        'product_id': [201, 202, 203, 204, 205, 206, 201, 207, 202, 208],
        'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'USB-Cable', 
                        'Headphones', 'Laptop', 'Webcam', 'Mouse', 'Printer'],
        'quantity': [2, 3, 1, 2, 5, 2, 1, 3, 2, 1],
        'price': [1500.50, 25.99, 89.99, 450.00, 15.50, 
                 79.99, 1500.50, 120.00, 25.99, 350.00],
        'order_date': ['2026-01-15', '2026-01-15', '2026-01-16', '2026-01-16', 
                      '2026-01-17', '2026-01-17', '2026-01-18', '2026-01-18',
                      '2026-01-19', '2026-01-20']
    }
    return pd.DataFrame(data)

def extract_from_csv(file_path: str) -> pd.DataFrame:
    """
    استخراج البيانات من ملف CSV مع معالجة جميع الأخطاء
    """
    # 1. التحقق من وجود الملف
    if not os.path.exists(file_path):
        print(f"⚠️ الملف {file_path} غير موجود! سيتم استخدام بيانات تجريبية.")
        return create_default_data()
    
    # 2. التحقق من حجم الملف
    if os.path.getsize(file_path) == 0:
        print(f"⚠️ الملف {file_path} فارغ! سيتم استخدام بيانات تجريبية.")
        return create_default_data()
    
    # 3. محاولة قراءة الملف مع معالجة الأخطاء
    try:
        # قراءة الملف مع تحديد رؤوس الأعمدة
        df = pd.read_csv(file_path)
        
        # التحقق من وجود بيانات
        if df.empty:
            print("⚠️ الملف لا يحتوي على بيانات! سيتم استخدام بيانات تجريبية.")
            return create_default_data()
            
        # التحقق من وجود أعمدة
        if len(df.columns) == 0:
            print("⚠️ الملف لا يحتوي على أعمدة! سيتم استخدام بيانات تجريبية.")
            return create_default_data()
            
        print(f"✅ تم قراءة {len(df)} سجل من الملف")
        return df
        
    except pd.errors.EmptyDataError:
        print("⚠️ خطأ: الملف فارغ أو تالف! سيتم استخدام بيانات تجريبية.")
        return create_default_data()
        
    except Exception as e:
        print(f"⚠️ خطأ غير متوقع: {e}")
        print("سيتم استخدام بيانات تجريبية.")
        return create_default_data()

def extract_from_api(url: str) -> pd.DataFrame:
    """
    استخراج البيانات من API مع معالجة الأخطاء
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print("⚠️ لم يتم استلام بيانات من الـ API! سيتم استخدام بيانات تجريبية.")
            return create_default_data()
            
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"⚠️ خطأ في الـ API: {e}")
        print("سيتم استخدام بيانات تجريبية.")
        return create_default_data()

# دالة مساعدة لحفظ البيانات في ملف (اختياري)
def save_sample_data(file_path: str = "data/raw/orders.csv"):
    """حفظ بيانات تجريبية في ملف"""
    df = create_default_data()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
    print(f"✅ تم حفظ بيانات تجريبية في {file_path}")
    return df

# إذا تم تشغيل الملف مباشرة، سيتم إنشاء بيانات تجريبية
if __name__ == "__main__":
    save_sample_data()
    print("\n📊 عينة من البيانات:")
    df = pd.read_csv("data/raw/orders.csv")
    print(df.head())