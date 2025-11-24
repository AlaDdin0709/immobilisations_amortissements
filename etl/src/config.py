"""Configuration centralisée pour le pipeline ETL.

Ce module charge les variables d'environnement et définit
les paramètres de connexion API et base de données.
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de l'API OpenData Paris
DATASET_ID = os.getenv('DATASET_ID', 'immobilisations-etat-des-amortissements')
API_URL = os.getenv('DATASET_API_URL', 'https://opendata.paris.fr/api/records/1.0/search')        
SEARCH_URL = os.getenv('SEARCH_URL', 'https://opendata.paris.fr/api/records/1.0/search')

# Configuration de la base de données MySQL
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
DB_HOST = os.getenv('MYSQL_HOST', 'mysql')
DB_PORT = os.getenv('MYSQL_PORT', '3306')
DB_NAME = os.getenv('MYSQL_DATABASE', 'immobilisations_amortissements')

# URL de connexion SQLAlchemy
DB_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Taille des lots pour l'extraction par pagination
BATCH_SIZE = int(os.getenv('EXTRACTION_BATCH_SIZE', 1000))