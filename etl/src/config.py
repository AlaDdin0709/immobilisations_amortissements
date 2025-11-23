import os
from dotenv import load_dotenv


load_dotenv()

DATASET_ID = os.getenv('DATASET_ID', 'immobilisations-etat-des-amortissements')
API_URL = os.getenv('DATASET_API_URL', 'https://opendata.paris.fr/api/records/1.0/search')        
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'immobilisations_amortissements')
DB_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SEARCH_URL = os.getenv('SEARCH_URL', 'https://opendata.paris.fr/api/records/1.0/search')
BATCH_SIZE = int(os.getenv('EXTRACTION_BATCH_SIZE', 1000))