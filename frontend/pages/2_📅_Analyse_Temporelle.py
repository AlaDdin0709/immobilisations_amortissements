import streamlit as st
from PIL import Image
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Analyse Temporelle - Dashboards",
    page_icon="📅",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
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
    
    .dashboard-header {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border-left: 6px solid #764ba2;
    }
    
    .dashboard-header h1 {
        color: #1e293b !important;
        font-size: 2.5rem;
        margin: 0;
    }
    
    .dashboard-header p {
        color: #64748b !important;
    }
    
    .chart-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .chart-card h4 {
        color: #1e293b !important;
        background: none !important;
        padding: 0 !important;
        margin-bottom: 0.5rem;
    }
    
    .chart-card p {
        color: #64748b !important;
        background: none !important;
        padding: 0 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8fafc;
        border-radius: 8px;
        color: #475569;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        color: white;
    }
    
    h3, h4 {
        color: white !important;
        background: rgba(255, 255, 255, 0.15);
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Chemin vers les dashboards
DASHBOARD_DIR = Path(__file__).parent.parent / "Dashboards" / "ANALYSE TEMPORELLE"

# Informations sur le dashboard
DASHBOARD_INFO = {
    "icon": "📅",
    "color": "#764ba2",
    "description": "Évolution temporelle et analyse des tendances",
    "charts": [
        {
            "title": "Dashboard Complet",
            "file": "ANALYSE TEMPORELLE dashboard.jpg",
            "description": "Vue d'ensemble complète du tableau de bord"
        },
        {
            "title": "Acquisitions par Année",
            "file": "acquisitions-par-annee.jpg",
            "description": "Évolution annuelle des acquisitions"
        },
        {
            "title": "Acquisitions par Trimestre",
            "file": "acquisitions-par-trimestre.jpg",
            "description": "Répartition trimestrielle des acquisitions"
        },
        {
            "title": "Acquisitions par Mois",
            "file": "nombre-dacquisitions-par-mois-annee.jpg",
            "description": "Distribution mensuelle des acquisitions par année"
        },
        {
            "title": "Amortissement Cumulé",
            "file": "amortissement-cumule.jpg",
            "description": "Évolution de l'amortissement cumulé"
        }
    ]
}

def load_image(image_path):
    """Charge une image avec gestion d'erreur"""
    try:
        if image_path.exists():
            return Image.open(image_path)
        else:
            st.error(f"Image non trouvée: {image_path.name}")
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image: {e}")
        return None

# Header
st.markdown(f"""
<div class="dashboard-header">
    <h1>{DASHBOARD_INFO['icon']} Analyse Temporelle</h1>
    <p style="color: #64748b; font-size: 1.1rem; margin-top: 0.5rem;">{DASHBOARD_INFO['description']}</p>
</div>
""", unsafe_allow_html=True)

# Mode d'affichage
view_mode = st.radio(
    "Mode d'affichage",
    ["📊 Dashboard Complet", "📈 Graphiques Détaillés"],
    horizontal=True,
    help="Choisissez le mode de visualisation"
)

st.markdown("---")

if view_mode == "📊 Dashboard Complet":
    # Affichage du dashboard complet
    dashboard_file = DASHBOARD_DIR / "ANALYSE TEMPORELLE dashboard.jpg"
    dashboard_img = load_image(dashboard_file)
    
    if dashboard_img:
        st.markdown("### 📊 Vue d'Ensemble")
        st.image(dashboard_img, use_column_width=True)
        
        # Bouton de téléchargement
        with open(dashboard_file, "rb") as file:
            btn = st.download_button(
                label="📥 Télécharger le Dashboard",
                data=file,
                file_name="analyse_temporelle_dashboard.jpg",
                mime="image/jpeg"
            )
    else:
        st.warning("Le dashboard complet n'est pas disponible actuellement.")

elif view_mode == "📈 Graphiques Détaillés":
    # Affichage des graphiques individuels avec onglets
    st.markdown("### 📈 Graphiques Détaillés")
    
    # Créer les onglets pour chaque graphique (sauf le dashboard complet)
    chart_list = [chart for chart in DASHBOARD_INFO['charts'] if chart['title'] != "Dashboard Complet"]
    tab_names = [chart['title'] for chart in chart_list]
    tabs = st.tabs(tab_names)
    
    for tab, chart in zip(tabs, chart_list):
        with tab:
            chart_file = DASHBOARD_DIR / chart['file']
            chart_img = load_image(chart_file)
            
            if chart_img:
                st.markdown(f"""
                <div class="chart-card">
                    <h4>{chart['title']}</h4>
                    <p style="color: #64748b;">{chart['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.image(chart_img, use_column_width=True)
                
                # Informations sur l'image
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"📄 {chart['file']}")
                with col2:
                    with open(chart_file, "rb") as file:
                        st.download_button(
                            label="📥 Télécharger",
                            data=file,
                            file_name=chart['file'],
                            mime="image/jpeg",
                            key=f"download_{chart['file']}"
                        )
            else:
                st.warning(f"Le graphique '{chart['title']}' n'est pas disponible actuellement.")



# Informations complémentaires
st.markdown("---")
st.markdown("### 💡 À propos de ce dashboard")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **Analyse Temporelle** offre une vision détaillée de l'évolution dans le temps :
    
    - 📅 **Tendances annuelles** : Évolution des acquisitions année après année
    - 📊 **Saisonnalité** : Identification des patterns trimestriels et mensuels
    - 💹 **Amortissement** : Suivi de l'amortissement cumulé
    - 🔍 **Granularité** : Analyse du niveau annuel au niveau mensuel
    """)

with col2:
    st.success("""
    **Formats disponibles :**
    - Images haute résolution (JPEG)
    - Dashboard complet
    - Graphiques individuels
    - Téléchargement disponible
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 1rem;">
    <p style="font-size: 0.9rem;">📅 Analyse Temporelle - Tableau de Bord Immobilisations</p>
</div>
""", unsafe_allow_html=True)


