"""
Page d'accueil de l'application Streamlit - Analyse des Immobilisations de Paris
"""
import streamlit as st
import os

st.set_page_config(
    page_title="Paris Immobilisations - Accueil",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Analyse des Immobilisations - Ville de Paris")

st.markdown("""
## Bienvenue sur le tableau de bord d'analyse

Cette application présente l'analyse des données d'immobilisations et amortissements de la Ville de Paris.

### 📊 Dashboards disponibles

Utilisez le menu latéral pour accéder aux différents dashboards :

1. **Vue Exécutive** - Vision globale et KPIs principaux
2. **Analyse Temporelle** - Évolution dans le temps des acquisitions et amortissements

### 🔧 Technologies utilisées

- **ETL** : Extraction et transformation des données OpenData Paris
- **Base de données** : MySQL
- **Visualisation** : Apache Superset
- **Interface** : Streamlit

### 📈 Source des données

Les données proviennent du jeu de données ouvert de la Ville de Paris :
**"Immobilisations - État des amortissements"**

---

👈 **Sélectionnez un dashboard dans le menu latéral pour commencer l'analyse**
""")

# Display connection info
st.sidebar.success("Sélectionnez un dashboard ci-dessus")

# Optional: Add some stats if database is available
try:
    import pandas as pd
    from sqlalchemy import create_engine
    
    def get_engine():
        user = os.getenv('MYSQL_USER', 'root')
        pw = os.getenv('MYSQL_PASSWORD')
        host = os.getenv('MYSQL_HOST', 'mysql')
        port = os.getenv('MYSQL_PORT', 3306)
        db = os.getenv('MYSQL_DATABASE')
        url = f'mysql+pymysql://{user}:{pw}@{host}:{port}/{db}'
        return create_engine(url)
    
    engine = get_engine()
    
    # Get quick stats
    stats_query = """
    SELECT 
        COUNT(*) as total_actifs,
        COUNT(DISTINCT collectivite) as nb_collectivites,
        SUM(valeur_acquisition) as valeur_totale
    FROM immobilisations_amortissements
    """
    
    stats = pd.read_sql(stats_query, engine)
    
    st.markdown("### 📊 Statistiques Générales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total d'actifs", f"{int(stats['total_actifs'].iloc[0]):,}")
    
    with col2:
        st.metric("Collectivités", int(stats['nb_collectivites'].iloc[0]))
    
    with col3:
        valeur = stats['valeur_totale'].iloc[0]
        if pd.notna(valeur):
            st.metric("Valeur totale", f"{valeur:,.0f} €")
        else:
            st.metric("Valeur totale", "N/A")
            
except Exception as e:
    st.info("💡 Les statistiques seront disponibles une fois l'ETL exécuté")
