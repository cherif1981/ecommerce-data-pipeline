import pandas as pd
import os
import sys
import traceback

# Ajouter le dossier src au chemin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.extract import extract_from_csv, create_default_data
    from src.validate import validate_data
    from src.transform import transform_data
    from src.load import load_to_db
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    print("Assurez-vous que tous les fichiers sont présents dans le dossier src/")
    sys.exit(1)

def ensure_data_exists():
    """Vérifier que les données existent et sont valides"""
    file_path = "data/raw/orders.csv"
    
    try:
        # Si le fichier n'existe pas
        if not os.path.exists(file_path):
            print(f"⚠️ Le fichier {file_path} n'existe pas. Création de données de test...")
            df = create_default_data()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_csv(file_path, index=False)
            print(f"✅ Données de test créées dans {file_path}")
            return df
        
        # Si le fichier est vide
        if os.path.getsize(file_path) == 0:
            print(f"⚠️ Le fichier {file_path} est vide. Création de données de test...")
            df = create_default_data()
            df.to_csv(file_path, index=False)
            print(f"✅ Données de test créées dans {file_path}")
            return df
        
        # Tentative de lecture du fichier
        df = pd.read_csv(file_path)
        if df.empty or len(df.columns) == 0:
            raise ValueError("Le fichier est corrompu ou vide")
        
        print(f"✅ {len(df)} enregistrements chargés depuis {file_path}")
        return df
        
    except Exception as e:
        print(f"❌ Erreur de lecture du fichier : {e}")
        print("🔄 Création de données de test...")
        df = create_default_data()
        df.to_csv(file_path, index=False)
        print(f"✅ Données de test créées dans {file_path}")
        return df

def run_pipeline():
    """Exécuter le pipeline ETL"""
    print("\n" + "="*60)
    print("🚀 Démarrage du Pipeline ETL...")
    print("="*60 + "\n")
    
    try:
        # Étape 1 : Chargement des données
        print("📥 Étape 1 : Chargement des données...")
        df = ensure_data_exists()
        if df is None or df.empty:
            print("❌ Aucune donnée à traiter !")
            return
        
        print(f"📊 {len(df)} enregistrements chargés")
        print("\nAperçu des données :")
        print(df.head())
        print("\n" + "-"*60)
        
        # Étape 2 : Validation des données
        print("🔍 Étape 2 : Validation de la qualité des données...")
        try:
            if validate_data(df):
                print("✅ Les données sont valides et prêtes à être traitées")
            else:
                print("⚠️ Des problèmes ont été détectés mais le traitement continue")
        except Exception as e:
            print(f"⚠️ Avertissement lors de la validation : {e}")
            print("🔄 Le traitement continue malgré l'avertissement...")
        
        print("\n" + "-"*60)
        
        # Étape 3 : Transformation des données
        print("🔄 Étape 3 : Transformation des données...")
        try:
            df_transformed = transform_data(df)
            print(f"✅ Données transformées ({len(df_transformed)} enregistrements)")
            print("\nAperçu des données transformées :")
            print(df_transformed.head())
        except Exception as e:
            print(f"❌ Échec de la transformation : {e}")
            traceback.print_exc()
            return
        
        print("\n" + "-"*60)
        
        # Étape 4 : Chargement dans la base de données
        print("💾 Étape 4 : Chargement des données dans la base...")
        try:
            load_to_db(df_transformed, "orders")
            print("✅ Données chargées avec succès")
        except Exception as e:
            print(f"❌ Échec du chargement : {e}")
            traceback.print_exc()
            return
        
        print("\n" + "-"*60)
        print("🎉 Le Pipeline est terminé avec succès !")
        print("="*60 + "\n")
        
        # Affichage des statistiques
        print("📊 Statistiques rapides :")
        print(f"   - Nombre de commandes : {len(df_transformed)}")
        if 'customer_id' in df_transformed.columns:
            print(f"   - Clients uniques : {df_transformed['customer_id'].nunique()}")
        if 'product_id' in df_transformed.columns:
            print(f"   - Produits uniques : {df_transformed['product_id'].nunique()}")
        if 'total_amount' in df_transformed.columns:
            print(f"   - Total des ventes : ${df_transformed['total_amount'].sum():,.2f}")
        
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\n⏹️ Programme arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur critique : {e}")
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")