import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title='Paris OpenData Analytics')
st.title('Paris OpenData Analytics - Squelette')

st.markdown('Cette interface affiche des KPIs après que l\'ETL ait chargé les données dans MySQL.')

@st.cache_data
def get_engine():
    user = os.getenv('MYSQL_USER', 'root')
    pw = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST', 'mysql')
    port = os.getenv('MYSQL_PORT', 3306)
    db = os.getenv('MYSQL_DATABASE')
    url = f'mysql+pymysql://{user}:{pw}@{host}:{port}/{db}'
    return create_engine(url)

try:
    engine = get_engine()
    # Show a sample from the main ETL target table
    df = pd.read_sql('SELECT * FROM immobilisations_amortissements LIMIT 10', engine)
    st.write('Aperçu des données')
    st.dataframe(df)
except Exception as e:
    st.warning('Impossible de lire les données depuis MySQL (vérifier que l\'ETL a été exécuté):')
    st.text(str(e))

st.markdown('---')
st.markdown('Prochaines étapes : implémenter KPIs, charts Plotly et intégration Superset.')
