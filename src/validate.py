import pandas as pd

def validate_data(df: pd.DataFrame) -> bool:
    """
    التحقق من جودة البيانات
    """
    print("🔍 جاري التحقق من جودة البيانات...")
    
    errors = []
    
    # 1. التحقق من وجود أعمدة مطلوبة
    required_columns = ['order_id', 'customer_id', 'product_id', 'product_name', 
                       'quantity', 'price', 'order_date']
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"العمود '{col}' غير موجود")
    
    if errors:
        print(f"❌ أخطاء في بنية البيانات: {', '.join(errors)}")
        return False
    
    # 2. التحقق من وجود قيم فارغة في الأعمدة المهمة
    if df['order_id'].isnull().any():
        errors.append("يوجد Order ID فارغ!")
    
    if df['customer_id'].isnull().any():
        errors.append("يوجد Customer ID فارغ!")
    
    # 3. التحقق من أن الأسعار موجبة
    if (df['price'] <= 0).any():
        errors.append("يوجد سعر أقل من أو يساوي صفر!")
    
    # 4. التحقق من أن الكميات موجبة
    if (df['quantity'] <= 0).any():
        errors.append("يوجد كمية أقل من أو تساوي صفر!")
    
    # 5. التحقق من أن التاريخ بصيغة صحيحة
    try:
        pd.to_datetime(df['order_date'])
    except:
        errors.append("صيغة التاريخ غير صحيحة!")
    
    if errors:
        print(f"❌ تم العثور على {len(errors)} مشكلة:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ جميع الفحوصات اجتازت بنجاح!")
    return True