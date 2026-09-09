import pandas as pd

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    تنظيف وتحويل البيانات
    """
    print("🔄 جاري تحويل البيانات...")
    
    # عمل نسخة من البيانات
    df_transformed = df.copy()
    
    # 1. إزالة المكررات
    before = len(df_transformed)
    df_transformed = df_transformed.drop_duplicates(subset=['order_id'])
    after = len(df_transformed)
    if before != after:
        print(f"   - تم إزالة {before - after} سجل مكرر")
    
    # 2. تحويل عمود التاريخ
    df_transformed['order_date'] = pd.to_datetime(df_transformed['order_date'])
    
    # 3. إنشاء عمود السنة والشهر للتحليلات
    df_transformed['year'] = df_transformed['order_date'].dt.year
    df_transformed['month'] = df_transformed['order_date'].dt.month
    
    # 4. حساب إجمالي الطلب (الكمية * السعر)
    df_transformed['total_amount'] = df_transformed['quantity'] * df_transformed['price']
    
    # 5. ترتيب البيانات حسب التاريخ
    df_transformed = df_transformed.sort_values('order_date')
    
    print(f"   - عدد السجلات بعد التحويل: {len(df_transformed)}")
    print("✅ تم تحويل البيانات بنجاح")
    
    return df_transformed