# Paris OpenData Analytics (squelette)

But: créer une plateforme d'analyse de données automatisée, dockerisée, et conforme aux 12 Factor App.

Structure initiale:
- `etl/` : service ETL Python (extraction → transformation → load)
- `mysql/` : initialisation base MySQL
- `superset/` : fichiers de config et import de dashboards
- `frontend/` : Streamlit UI

Démarrage rapide (après configuration de `.env`):

```powershell
# depuis la racine du projet
cp .env.example .env
# éditer .env et fournir DATASET_API_URL et mots de passe
docker-compose up --build
```

Prochaines étapes:
- Implémenter l'ETL (extraction depuis OpenData Paris)
- Concevoir le schéma MySQL (optimisé)
- Configurer Superset pour importer datasets & dashboards
- Créer frontend Streamlit pour KPI & intégration Superset

Voir les fichiers créés dans le repo pour le squelette initial.
