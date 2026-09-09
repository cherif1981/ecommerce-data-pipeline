from flask import Flask, render_template_string, Markup
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# قراءة البيانات
engine = create_engine('sqlite:///ecommerce.db')
df = pd.read_sql('SELECT * FROM orders;', engine)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard E-Commerce</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        .stats { display: flex; gap: 20px; justify-content: center; margin: 30px 0; }
        .card { 
            background: white; 
            padding: 20px 40px; 
            border-radius: 10px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 150px;
        }
        .card h3 { margin: 0; color: #666; font-size: 14px; }
        .card h2 { margin: 10px 0 0 0; color: #2c3e50; }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }
        th { 
            background-color: #3498db; 
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f1f1f1; }
        .container { max-width: 1200px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Tableau de Bord E-Commerce</h1>
        
        <div class="stats">
            <div class="card">
                <h3>💰 Total des ventes</h3>
                <h2>${{ total_ventes }}</h2>
            </div>
            <div class="card">
                <h3>📦 Nombre de commandes</h3>
                <h2>{{ nb_commandes }}</h2>
            </div>
            <div class="card">
                <h3>👥 Clients uniques</h3>
                <h2>{{ nb_clients }}</h2>
            </div>
            <div class="card">
                <h3>📦 Produits uniques</h3>
                <h2>{{ nb_produits }}</h2>
            </div>
        </div>
        
        <h2 style="margin-top: 30px;">📋 Dernières commandes</h2>
        {{ table_html|safe }}
        
        <p style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            Mise à jour : {{ date }}
        </p>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    # Convertir le DataFrame en HTML
    table_html = df.to_html(
        index=False, 
        classes='dataframe',
        border=0,
        justify='center'
    )
    
    return render_template_string(
        HTML_TEMPLATE,
        total_ventes=f"{df['total_amount'].sum():,.2f}",
        nb_commandes=len(df),
        nb_clients=df['customer_id'].nunique(),
        nb_produits=df['product_id'].nunique(),
        table_html=Markup(table_html),
        date=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')