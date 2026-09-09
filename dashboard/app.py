import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from src.config import DB_CONFIG

st.title("📊 E-Commerce Dashboard")

# الاتصال بقاعدة البيانات
conn_str = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(conn_str)

# تحميل البيانات
@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM orders", engine)

df = load_data()

# إظهار الإحصائيات
col1, col2, col3 = st.columns(3)
col1.metric("💰 إجمالي الإيرادات", f"${df['total_amount'].sum():,.2f}")
col2.metric("📦 إجمالي الطلبات", len(df))
col3.metric("👥 عدد العملاء", df['customer_id'].nunique())

# رسم بياني للمبيعات اليومية
st.subheader("المبيعات اليومية")
daily_sales = df.groupby('order_date')['total_amount'].sum().reset_index()
st.line_chart(daily_sales.set_index('order_date'))