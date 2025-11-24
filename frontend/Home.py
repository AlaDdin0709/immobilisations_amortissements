import streamlit as st
from PIL import Image
from pathlib import Path
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord Immobilisations",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé moderne
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        box-shadow: 4px 0 20px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #e0e7ff !important;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1600px;
    }
    
    .header-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border-left: 6px solid #667eea;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    .dashboard-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);
    }
    
    .dashboard-card h3 {
        color: #1e293b !important;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .dashboard-card p, .dashboard-card ul, .dashboard-card li {
        color: #475569 !important;
    }
    
    [data-testid="stMetric"] {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    [data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-size: 2rem !important;
    }
    
    h3, h4 {
        color: white !important;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Chemin vers les dashboards
DASHBOARD_DIR = Path(__file__).parent / "Dashboards"

def count_dashboard_images():
    """Compte le nombre d'images dans les dashboards"""
    try:
        vue_exec = DASHBOARD_DIR / "VUE EXÉCUTIVE"
        analyse_temp = DASHBOARD_DIR / "ANALYSE TEMPORELLE"
        
        vue_count = len(list(vue_exec.glob("*.jpg"))) if vue_exec.exists() else 0
        analyse_count = len(list(analyse_temp.glob("*.jpg"))) if analyse_temp.exists() else 0
        
        return vue_count, analyse_count
    except:
        return 0, 0

# Sidebar
with st.sidebar:
    st.markdown("# 📊 Navigation")
    st.markdown("---")
    
    st.markdown("### 📁 Dashboards Disponibles")
    st.info("""
    - 👁️ **Vue Exécutive**
    - 📅 **Analyse Temporelle**
    
    Utilisez le menu ci-dessus pour naviguer.
    """)
    
    st.markdown("---")
    st.markdown(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Header
st.markdown("""
<div class="header-card">
    <h1 class="header-title">📊 Tableau de Bord Immobilisations</h1>
    <p class="header-subtitle">Vue d'ensemble et analyse des actifs immobilisés</p>
</div>
""", unsafe_allow_html=True)

# Statistiques des dashboards
st.markdown("### 📈 Contenu Disponible")
vue_count, analyse_count = count_dashboard_images()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👁️ Vue Exécutive", f"{vue_count} graphiques", help="Nombre de visualisations disponibles")

with col2:
    st.metric("📅 Analyse Temporelle", f"{analyse_count} graphiques", help="Nombre de visualisations disponibles")

with col3:
    st.metric("📊 Total", f"{vue_count + analyse_count} images", help="Total des dashboards disponibles")

st.markdown("---")

# Aperçu des dashboards disponibles
st.markdown("### 🎯 Dashboards Disponibles")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="dashboard-card">
        <h3>👁️ Vue Exécutive</h3>
        <p>Vue d'ensemble stratégique des actifs immobilisés avec indicateurs clés de performance.</p>
        <ul>
            <li>Nombre total d'actifs</li>
            <li>Acquisitions par année</li>
            <li>Répartition par nature</li>
            <li>Top 10 par valeur</li>
            <li>Valeur par collectivité</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="dashboard-card">
        <h3>📅 Analyse Temporelle</h3>
        <p>Évolution temporelle et analyse des tendances d'acquisition et d'amortissement.</p>
        <ul>
            <li>Acquisitions par année</li>
            <li>Acquisitions par trimestre</li>
            <li>Acquisitions par mois</li>
            <li>Amortissement cumulé</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Instructions
st.markdown("### 💡 Comment utiliser")
st.info("""
**Navigation :**
- Utilisez le menu latéral pour accéder aux différents dashboards
- Chaque dashboard affiche une vue complète ainsi que des graphiques individuels

**Modes d'affichage :**
- **Vue Dashboard** : Aperçu complet du tableau de bord
- **Graphiques Détaillés** : Analyse détaillée de chaque indicateur

**Images :**
- Toutes les visualisations sont des images statiques exportées depuis Superset
- Téléchargement disponible pour chaque graphique
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem;">
    <p style="font-size: 1.1rem; font-weight: 600;">📊 Tableau de Bord Immobilisations</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">Visualisations exportées depuis Superset</p>
</div>
""", unsafe_allow_html=True)
