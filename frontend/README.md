# Application Streamlit - Visualisation des Dashboards

Cette application Streamlit présente les dashboards Superset de manière intégrée.

## Structure

- `Home.py` : Page d'accueil avec statistiques générales
- `pages/1_📊_Vue_Executive.py` : Dashboard Vue Exécutive
- `pages/2_📅_Analyse_Temporelle.py` : Dashboard Analyse Temporelle

## Fonctionnalités

### 1. Embedding des dashboards Superset

Chaque page de dashboard affiche :
- Un iframe intégrant le dashboard Superset via `st.components.v1.iframe()` (méthode recommandée)
- Des visualisations alternatives créées directement depuis MySQL (fallback)
- Des métriques clés extraites de la base de données
- Gestion d'erreur avec lien de secours pour ouvrir dans un nouvel onglet

### 2. Pages multi-navigables

Streamlit crée automatiquement un menu latéral pour naviguer entre les pages.

### 3. Variables d'environnement

Configuration via `docker-compose.yml` :
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` : connexion MySQL
- `SUPERSET_HOST` : URL de l'instance Superset (par défaut: `http://superset:8088`)
- `SUPERSET_DASHBOARD_ID_EXECUTIVE` : ID du dashboard Vue Exécutive (par défaut: `1`)
- `SUPERSET_DASHBOARD_ID_TEMPORAL` : ID du dashboard Analyse Temporelle (par défaut: `2`)

## Utilisation

### Lancer l'application

```bash
docker-compose up -d streamlit
```

### Accéder à l'application

Ouvrez votre navigateur : http://localhost:8501

**Note** : Utilisez `localhost` et non `0.0.0.0` pour accéder à l'application depuis votre navigateur.

### Navigation

1. La page d'accueil affiche des statistiques générales
2. Utilisez le menu latéral pour accéder aux dashboards :
   - 📊 Vue Exécutive
   - 📅 Analyse Temporelle

## Configuration de l'embedding Superset

Pour que les iframes fonctionnent correctement, vous devez :

### Option 1 : Activer l'embedding dans Superset (recommandé)

Ajouter dans `superset_config.py` :

```python
# Enable embedding
FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
    "EMBEDDABLE_CHARTS": True
}

# Allow iframe embedding
HTTP_HEADERS = {
    'X-Frame-Options': 'ALLOWALL'
}

# Or use SAMEORIGIN if both services sont sur le même domaine
# HTTP_HEADERS = {'X-Frame-Options': 'SAMEORIGIN'}
```

### Option 2 : Utiliser les liens directs

Si l'embedding ne fonctionne pas, l'utilisateur peut :
1. Cliquer sur le lien fourni dans la page
2. Se connecter à Superset dans un nouvel onglet
3. Consulter les dashboards directement dans Superset

### Option 3 : Utiliser les visualisations alternatives

Chaque page affiche également des graphiques créés directement depuis les données MySQL avec Plotly, qui servent de fallback si Superset n'est pas accessible.

## Notes techniques

- Les dashboards Superset doivent être créés et publiés avant utilisation
- Les IDs des dashboards peuvent être trouvés dans l'URL Superset : `/superset/dashboard/{ID}/`
- Les visualisations alternatives utilisent Plotly et requièrent que l'ETL ait peuplé la base MySQL
