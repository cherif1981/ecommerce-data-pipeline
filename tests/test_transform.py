import pandas as pd
from src.transform import transform_data

def test_transform_data():
    # بيانات وهمية
    df = pd.DataFrame({
        'order_id': [1, 2, 1],  # مكرر
        'quantity': [2, 1, 3],
        'price': [10, 20, 15],
        'order_date': ['2023-01-01', '2023-01-02', '2023-01-01']
    })
    
    df_transformed = transform_data(df)
    
    # يجب إزالة المكرر (يصبح لدينا صفان فقط)
    assert len(df_transformed) == 2
    # يجب حساب total_amount بشكل صحيح
    assert df_transformed['total_amount'].iloc[0] == 20