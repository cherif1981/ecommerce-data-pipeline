# 📊 E-Commerce Data Pipeline

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-blue)

## 🚀 À propos du projet

Ce projet est un pipeline **ETL (Extract, Transform, Load)** pour l'analyse de données e-commerce. Il permet de :

- **Extraire** des données depuis des fichiers CSV
- **Valider** la qualité des données
- **Transformer** les données (calculs, agrégations)
- **Charger** les données dans une base SQLite
- **Analyser** les données avec des requêtes SQL
- **Visualiser** les données via un Dashboard web

## 🛠️ Technologies utilisées

| Technologie     | Utilité                                    |
| --------------- | ------------------------------------------ |
| **Python 3.7+** | Langage principal                          |
| **Pandas**      | Manipulation et transformation des données |
| **SQLAlchemy**  | ORM pour la base de données                |
| **SQLite**      | Base de données légère                     |
| **Flask**       | Dashboard web                              |
| **Docker**      | Conteneurisation et déploiement            |
| **Pytest**      | Tests automatisés                          |
| **GitHub Actions** | Intégration continue (CI/CD)            |

## 📁 Structure du projet

```
ecommerce-data-pipeline/
├── .github/workflows/       # Pipelines CI/CD (GitHub Actions)
├── dashboard/                # Application Flask (visualisation des données)
├── data/                     # Fichiers CSV bruts et/ou base SQLite générée
├── sql/                      # Requêtes SQL d'analyse
├── src/ecommerce_pipeline/   # Code source du pipeline (extract, transform, load)
├── tests/                    # Tests unitaires (pytest)
├── config.py                 # Configuration du projet (chemins, DB, etc.)
├── explore_db.py             # Script utilitaire d'exploration de la base
├── main.py                   # Point d'entrée du pipeline
├── Dockerfile                # Image Docker de l'application
├── docker-compose.yml        # Orchestration des services (app + dashboard)
├── Makefile                  # Commandes raccourcies (install, run, test...)
├── requirements.txt          # Dépendances Python
├── pyproject.toml            # Configuration du projet Python
├── pytest.ini                # Configuration des tests
├── .env.example               # Exemple de variables d'environnement
└── README.md
```

## ⚙️ Installation

### Prérequis
- Python 3.7 ou supérieur
- pip
- (optionnel) Docker et Docker Compose

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/cherif1981/ecommerce-data-pipeline.git
cd ecommerce-data-pipeline

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate   # sur Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# puis éditer .env avec vos propres valeurs
```

## ▶️ Utilisation

```bash
# Lancer le pipeline complet (extract -> transform -> load)
python main.py

# Explorer le contenu de la base de données générée
python explore_db.py
```

Si un `Makefile` est disponible, vous pouvez aussi utiliser des raccourcis, par exemple :

```bash
make install   # installer les dépendances
make run       # lancer le pipeline
make test      # lancer les tests
```

*(Adaptez ces commandes aux cibles réellement définies dans votre `Makefile`.)*

## 📊 Dashboard

Le dashboard Flask permet de visualiser les résultats de l'analyse :

```bash
cd dashboard
python app.py
```

Puis ouvrez votre navigateur à l'adresse indiquée dans la console (par défaut `http://localhost:5000`).

## 🐳 Utilisation avec Docker

```bash
docker-compose up --build
```

Cela construit l'image et démarre l'ensemble des services définis dans `docker-compose.yml`.

## 🧪 Tests

Les tests sont écrits avec `pytest` :

```bash
pytest
```

## 🔄 Intégration continue

Un workflow GitHub Actions (`.github/workflows/`) exécute automatiquement les tests à chaque push / pull request.

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Poussez la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## ✍️ Auteur

**cherif1981** — [GitHub](https://github.com/cherif1981)
