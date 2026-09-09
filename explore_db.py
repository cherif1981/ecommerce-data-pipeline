import pandas as pd
from sqlalchemy import create_engine

# Connexion à la base de données
engine = create_engine('sqlite:///ecommerce.db')

# Afficher toutes les tables
print("="*60)
print("📋 Tables dans la base de données :")
print("="*60)
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)
print(tables)
print("\n")

# Afficher les données de la table orders
print("="*60)
print("📊 Données de la table orders :")
print("="*60)
df = pd.read_sql("SELECT * FROM orders;", engine)
print(df)
print("\n")

# Afficher les statistiques rapides
print("="*60)
print("📈 Statistiques rapides :")
print("="*60)
print(f"Nombre de commandes : {len(df)}")
print(f"Total des ventes : ${df['total_amount'].sum():,.2f}")
print(f"Nombre de clients uniques : {df['customer_id'].nunique()}")
print(f"Nombre de produits uniques : {df['product_id'].nunique()}")