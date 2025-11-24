"""
Dashboard Vue Exécutive - KPIs principaux et vision globale
"""
import streamlit as st
import os

st.set_page_config(
    page_title="Vue Exécutive",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Vue Exécutive")

st.markdown("""
Ce dashboard présente une vision globale des immobilisations avec les KPIs principaux :
- Nombre total d'actifs
- Valeur d'acquisition totale par collectivité
- Top 10 des immobilisations par valeur
- Répartition par nature d'actif
- Total d'acquisition par année
""")

# Superset configuration
SUPERSET_HOST = os.getenv('SUPERSET_HOST', 'http://superset:8088')
SUPERSET_DASHBOARD_ID_EXECUTIVE = os.getenv('SUPERSET_DASHBOARD_ID_EXECUTIVE', '1')

st.markdown("---")

# Option 1: Using iframe (simple but requires Superset to allow embedding)
st.markdown("### Dashboard Superset - Vue Exécutive")

# Build the dashboard URL
dashboard_url = f"{SUPERSET_HOST}/superset/dashboard/{SUPERSET_DASHBOARD_ID_EXECUTIVE}/"

st.info(f"""
💡 **Pour visualiser ce dashboard :**

1. Ouvrez Superset dans un nouvel onglet : [{SUPERSET_HOST}]({SUPERSET_HOST})
2. Connectez-vous avec vos identifiants
3. Accédez au dashboard "VUE EXÉCUTIVE"

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


