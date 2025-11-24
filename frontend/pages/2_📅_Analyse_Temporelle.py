"""
Dashboard Analyse Temporelle - Évolution des acquisitions et amortissements
"""
import streamlit as st
import os

st.set_page_config(
    page_title="Analyse Temporelle",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Analyse Temporelle")

st.markdown("""
Ce dashboard présente l'évolution temporelle des immobilisations :
- Acquisitions par année
- Acquisitions par trimestre
- Nombre d'acquisitions par mois/année
- Amortissement cumulé dans le temps
""")

# Superset configuration
SUPERSET_HOST = os.getenv('SUPERSET_HOST', 'http://superset:8088')
SUPERSET_DASHBOARD_ID_TEMPORAL = os.getenv('SUPERSET_DASHBOARD_ID_TEMPORAL', '2')

st.markdown("---")

# Dashboard embedding
st.markdown("### Dashboard Superset - Analyse Temporelle")

# Build the dashboard URL
dashboard_url = f"{SUPERSET_HOST}/superset/dashboard/{SUPERSET_DASHBOARD_ID_TEMPORAL}/"

st.info(f"""
💡 **Pour visualiser ce dashboard :**

1. Ouvrez Superset dans un nouvel onglet : [{SUPERSET_HOST}]({SUPERSET_HOST})
2. Connectez-vous avec vos identifiants
3. Accédez au dashboard "ANALYSE TEMPORELLE"

Ou utilisez l'iframe ci-dessous si l'embedding est activé dans Superset.
""")

# Iframe embedding using st.components (recommended method)
import streamlit.components.v1 as components

iframe_height = 800

try:
    components.iframe(dashboard_url, height=iframe_height, scrolling=True)
except Exception as e:
    st.error(f"Impossible de charger le dashboard : {str(e)}")
    st.markdown(f"[Ouvrir le dashboard dans un nouvel onglet]({dashboard_url})")


