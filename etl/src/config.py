import os
from dotenv import load_dotenv


load_dotenv()

DATASET_ID = os.getenv('DATASET_ID', 'immobilisations-etat-des-amortissements')
API_URL = env.get('DATASET_API_URL', 'https://opendata.paris.fr/api/records/1.0/search')        
DB_USER = env.get('DB_USER', 'root')
DB_PASSWORD = env.get('DB_PASSWORD', '')
DB_HOST = env.get('DB_HOST', 'mysql')
DB_PORT = env.get('DB_PORT', '3306')
DB_NAME = env.get('DB_NAME', 'immobilisations_amortissements')
DB_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SEARCH_URL = os.getenv('SEARCH_URL', 'https://opendata.paris.fr/api/records/1.0/search')