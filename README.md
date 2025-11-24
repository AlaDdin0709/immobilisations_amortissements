# 📊 Plateforme d'Analyse des Immobilisations et Amortissements

## 🎯 Introduction

Cette plateforme d'analyse automatisée permet la visualisation et le suivi des immobilisations et amortissements à partir des données OpenData Paris. Le système extrait, transforme et charge (ETL) automatiquement les données publiques, puis les présente via une interface Streamlit intuitive avec des tableaux de bord interactifs générés par Apache Superset.

### Objectifs du Projet

- **Automatisation complète** : Pipeline ETL autonome pour la collecte et le traitement des données
- **Visualisation moderne** : Interface Streamlit avec dashboards statiques exportés depuis Superset
- **Architecture cloud-ready** : Conformité aux principes 12-Factor App
- **Production-ready** : Containerisation Docker, healthchecks, logging professionnel

### Fonctionnalités Principales

✅ **ETL Automatisé** : Extraction par batch depuis l'API OpenData Paris (1000 enregistrements/batch)  
✅ **Transformation Avancée** : Calcul automatique des champs dérivés (taux d'amortissement, âge, valeur restante)  
✅ **Base de Données MySQL** : Stockage optimisé avec indexes et contraintes  
✅ **Dashboards Superset** : Visualisations avancées (acquisitions, répartitions, analyses temporelles)  
✅ **Interface Streamlit** : Navigation intuitive avec 3 pages (Accueil, Vue Executive, Analyse Temporelle)  
✅ **Mode Statique** : Affichage des dashboards via images JPG (pas de requêtes SQL en temps réel)

---

## 🏗️ Architecture Complète

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLATEFORME D'ANALYSE                         │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   ETL        │────▶│   MySQL      │◀────│  Superset    │
│   Python     │     │   Database   │     │  Analytics   │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        │                     │                     ▼
        │                     │            ┌──────────────┐
        │                     └───────────▶│  Streamlit   │
        │                                  │  Frontend    │
        │                                  └──────────────┘
        │                                         │
        ▼                                         ▼
┌──────────────┐                         ┌──────────────┐
│ OpenData API │                         │   Utilisateur│
│ Paris        │                         │   Final      │
└──────────────┘                         └──────────────┘
```

### Services Docker Compose

| Service | Image/Build | Port | Rôle | Dépendances |
|---------|-------------|------|------|-------------|
| **mysql** | `mysql:8.0` | 3306 | Base de données principale | - |
| **db_init** | `mysql:8.0` | - | Initialisation du schéma | mysql (healthy) |
| **etl** | `./etl` (custom) | - | Pipeline ETL automatisé | mysql (healthy) |
| **superset** | `./superset` (custom) | 8088 | Plateforme BI et dashboards | mysql |
| **streamlit** | `./frontend` (custom) | 8501 | Interface utilisateur web | superset |
| **adminer** | `adminer:latest` | 8080 | Administration base de données | mysql |

### Stack Technique

#### Backend & Data
- **Python 3.11** : Langage principal pour ETL et frontend
- **MySQL 8.0** : Base de données relationnelle
- **SQLAlchemy** : ORM pour les interactions base de données
- **Pandas** : Manipulation et transformation des données
- **Apache Superset 3.1.0** : Plateforme de business intelligence

#### Frontend
- **Streamlit 1.29.0** : Framework web pour interface utilisateur
- **Pillow 10.1.0** : Traitement et affichage d'images

#### Infrastructure
- **Docker & Docker Compose** : Containerisation et orchestration
- **Git** : Contrôle de version (branche: `restore-V3`)

---

## 📁 Structure du Projet

```
immobilisations_amortissements/
│
├── docker-compose.yml          # Orchestration des services
├── .env.example                # Template de configuration
├── .gitignore                  # Fichiers exclus du versioning
├── README.md                   # Documentation (ce fichier)
│
├── etl/                        # 🔧 Pipeline ETL
│   ├── Dockerfile              # Image Python pour ETL
│   ├── requirements.txt        # Dépendances Python
│   ├── entrypoint.sh           # Script de démarrage
│   └── src/
│       ├── main.py             # Orchestrateur principal ETL
│       ├── config.py           # Configuration centralisée
│       ├── extract/
│       │   └── extract.py      # Extraction API OpenData
│       ├── transform/
│       │   └── transform.py    # Transformation et enrichissement
│       ├── load/
│       │   └── load.py         # Chargement MySQL
│       └── utils/
│           └── process.py      # Utilitaires de conversion
│
├── mysql/                      # 🗄️ Base de Données
│   ├── init.sql                # Schéma et initialisation
│   └── run-init.sh             # Script d'initialisation
│
├── superset/                   # 📈 Business Intelligence
│   ├── Dockerfile              # Image Superset personnalisée
│   ├── superset_config.py      # Configuration Superset
│   ├── init-superset.sh        # Initialisation automatique
│   └── dashboards/             # Exports des dashboards
│       ├── dashboard_executive.json
│       └── dashboard_temporel.json
│
├── frontend/                   # 🖥️ Interface Utilisateur
│   ├── Dockerfile              # Image Streamlit
│   ├── requirements.txt        # Dépendances légères
│   ├── Home.py                 # Page d'accueil
│   ├── pages/
│   │   ├── 1_👁️_Vue_Executive.py
│   │   └── 2_📅_Analyse_Temporelle.py
│   └── Dashboards/             # Images statiques des dashboards
│       ├── Executive/
│       │   ├── nombre-total-d-actifs.jpg
│       │   ├── acquisitions.jpg
│       │   ├── repartition.jpg
│       │   ├── top-10.jpg
│       │   ├── collectivite.jpg
│       │   └── full-dashboard.jpg
│       └── Temporel/
│           ├── acquisitions-annee.jpg
│           ├── acquisitions-trimestre.jpg
│           ├── acquisitions-mois.jpg
│           ├── amortissement-cumule.jpg
│           └── full-dashboard.jpg
│
└── notebooks/                  # 📓 Jupyter notebooks (analyse ad-hoc)
```

---

## 🔄 Pipeline ETL Détaillé

### 1️⃣ Extraction (`etl/src/extract/extract.py`)

**Source** : API OpenData Paris  
**Méthode** : Pagination automatique avec générateur Python  
**Batch Size** : 1000 enregistrements par requête  
**Gestion d'erreurs** : Retry sur timeout, fallback pour réponses liste

```python
def fetch_records_in_batches(rows=1000):
    """Générateur pour extraire les enregistrements par batch"""
    # Pagination automatique avec offset
    # Timeout 120s, gestion des erreurs 400/500
```

### 2️⃣ Transformation (`etl/src/transform/transform.py`)

**Schéma Cible** : 12 colonnes typées
- `ndeg_immobilisation` (string, PK)
- `publication` (string)
- `collectivite` (string)
- `nature` (string)
- `date_acquisition`, `date_mise_en_service`, `date_fin_amortissement` (date)
- `valeur_acquisition`, `valeur_residuelle`, `dotation_amortissement` (decimal)
- `duree_amortissement` (int)
- `informations_complementaires` (text)

**Champs Dérivés Calculés** :
- `taux_amortissement` : Taux annuel d'amortissement (%)
- `annee_acquisition`, `mois_acquisition`, `jour_acquisition`, `trimestre_acquisition`
- `age_immobilisation` : Âge en années depuis l'acquisition
- `amortissement_total` : Montant total amorti à ce jour
- `pct_valeur_restante` : Pourcentage de valeur résiduelle

**Flags Qualité** :
- `is_complete` : Tous les champs essentiels présents
- `is_depreciation_complete` : Amortissement terminé

### 3️⃣ Chargement (`etl/src/load/load.py`)

**Stratégie** : UPSERT (INSERT ... ON DUPLICATE KEY UPDATE)  
**Transaction** : Rollback automatique en cas d'erreur  
**Performance** : Bulk insert avec SQLAlchemy  
**Sanitization** : Conversion NaN/Infinity avant insertion

```python
def upsert_immobilisations(df, table_name):
    """Insertion en masse avec gestion des transactions"""
    # Auto-création de table si nécessaire
    # Rollback sur erreur
```

---

## 🎨 Interface Streamlit

### Architecture Multi-Pages

#### 🏠 **Page d'Accueil** (`Home.py`)
- **Statistiques** : Compteurs d'images par dashboard
- **Navigation** : Cards cliquables vers les dashboards
- **Design** : Gradient bleu (#667eea → #764ba2), cards blanches avec ombres

#### 👁️ **Vue Executive** (`1_👁️_Vue_Executive.py`)
- **Mode 1** : Dashboard complet (image unique)
- **Mode 2** : Graphiques détaillés en onglets
  - Nombre total d'actifs
  - Acquisitions
  - Répartition
  - Top 10
  - Par collectivité
- **Fonctionnalités** : Téléchargement individuel des images

#### 📅 **Analyse Temporelle** (`2_📅_Analyse_Temporelle.py`)
- **Mode 1** : Dashboard temporel complet
- **Mode 2** : Analyses détaillées
  - Acquisitions par année
  - Acquisitions par trimestre
  - Acquisitions par mois
  - Amortissement cumulé
- **Design** : Gradient violet, navigation par onglets

### Style Visuel

**Thème Principal** :
- Background : Gradient bleu (#667eea → #764ba2)
- Cards : Blanc avec ombres portées
- Sidebar : Gradient bleu foncé (#1e3a8a → #1e40af)
- Typographie : Titres noirs, texte gris (#475569)

---

## 🚀 Installation et Démarrage

### Prérequis

- **Docker** : Version 20.10+
- **Docker Compose** : Version 2.0+
- **Git** : Pour cloner le repository
- **Ports disponibles** : 3306 (MySQL), 8080 (Adminer), 8088 (Superset), 8501 (Streamlit)

### Configuration Initiale

1️⃣ **Cloner le repository**
```powershell
git clone <repository-url>
cd immobilisations_amortissements
git checkout restore-V3
```

2️⃣ **Configurer les variables d'environnement**
```powershell
# Copier le template
cp .env.example .env

# Éditer .env avec vos valeurs
notepad .env
```

**Variables essentielles à modifier** :
```bash
# Sécurité (OBLIGATOIRE à changer)
MYSQL_ROOT_PASSWORD=VotreMotDePasseSecurise123
MYSQL_PASSWORD=VotreMotDePasseUser456
SUPERSET_ADMIN_PASSWORD=VotreMotDePasseSupersetXYZ
SUPERSET_SECRET_KEY=VotreCleSecrete789ABC

# API OpenData Paris (obligatoire)
DATASET_API_URL=https://opendata.paris.fr/api/records/1.0/search/?dataset=immobilisations-incorporelles-amortissements-reprise
```

3️⃣ **Lancer la plateforme**
```powershell
# Build et démarrage de tous les services
docker-compose up -d --build

# Vérifier les statuts
docker-compose ps

# Suivre les logs (optionnel)
docker-compose logs -f
```

### Ordre de Démarrage

Docker Compose gère automatiquement les dépendances :
1. **MySQL** démarre en premier (healthcheck actif)
2. **db_init** initialise le schéma une fois MySQL prêt
3. **ETL** lance l'extraction après la base prête
4. **Superset** démarre en parallèle
5. **Streamlit** démarre après Superset
6. **Adminer** démarre en parallèle

### Accès aux Services

| Service | URL | Identifiants |
|---------|-----|-------------|
| **Streamlit** | http://localhost:8501 | - (pas d'auth) |
| **Superset** | http://localhost:8088 | `.env` SUPERSET_ADMIN_USER / SUPERSET_ADMIN_PASSWORD |
| **Adminer** | http://localhost:8080 | Serveur: mysql, User: `.env` MYSQL_USER |
| **MySQL** | localhost:3306 | User: `.env` MYSQL_USER |

---

## 🛠️ Opérations Courantes

### Relancer l'ETL Manuellement
```powershell
docker-compose restart etl
docker-compose logs -f etl
```

### Vérifier les Données MySQL
```powershell
# Via Adminer (interface web)
# → http://localhost:8080

# Via CLI
docker exec -it <mysql-container-id> mysql -u admin -p paris_immobilisations_db
```

### Rebuild un Service Spécifique
```powershell
# Exemple : reconstruire Streamlit après modification
docker-compose up -d --build streamlit
```

### Arrêter la Plateforme
```powershell
# Arrêt propre
docker-compose down

# Arrêt avec suppression des volumes (⚠️ perte de données)
docker-compose down -v
```

### Consulter les Logs
```powershell
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f etl
docker-compose logs -f streamlit

# Dernières 200 lignes
docker logs <container-name> --tail 200
```

---

## 📊 Schéma de Base de Données

### Table : `immobilisations`

```sql
CREATE TABLE IF NOT EXISTS immobilisations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ndeg_immobilisation VARCHAR(100) UNIQUE NOT NULL,
    publication VARCHAR(255),
    collectivite VARCHAR(255),
    nature VARCHAR(255),
    date_acquisition DATE,
    date_mise_en_service DATE,
    date_fin_amortissement DATE,
    valeur_acquisition DECIMAL(15,2),
    valeur_residuelle DECIMAL(15,2),
    dotation_amortissement DECIMAL(15,2),
    duree_amortissement INT,
    informations_complementaires TEXT,
    
    -- Champs dérivés calculés par l'ETL
    taux_amortissement DECIMAL(5,2),
    annee_acquisition INT,
    mois_acquisition INT,
    jour_acquisition INT,
    trimestre_acquisition INT,
    age_immobilisation DECIMAL(10,2),
    amortissement_total DECIMAL(15,2),
    pct_valeur_restante DECIMAL(5,2),
    
    -- Flags qualité
    is_complete BOOLEAN,
    is_depreciation_complete BOOLEAN,
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes pour performance
    INDEX idx_collectivite (collectivite),
    INDEX idx_nature (nature),
    INDEX idx_date_acquisition (date_acquisition),
    INDEX idx_annee_acquisition (annee_acquisition)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Volumétrie

- **~1000-5000 enregistrements** (selon disponibilité OpenData)
- **Refresh** : À chaque exécution ETL (UPSERT)
- **Indexes** : Optimisation des requêtes Superset

---

## ✅ Conformité 12-Factor App

| Facteur | Statut | Implémentation |
|---------|--------|----------------|
| **I. Codebase** | ✅ | Repository Git unique, branche `restore-V3` |
| **II. Dependencies** | ✅ | `requirements.txt` pour Python, images Docker versionnées |
| **III. Config** | ✅ | Variables d'environnement via `.env` (12-factor compliant) |
| **IV. Backing Services** | ✅ | MySQL, Superset traités comme ressources attachables |
| **V. Build/Release/Run** | ✅ | Docker build → Docker Compose up (séparation stricte) |
| **VI. Processes** | ✅ | Services stateless, état en base MySQL |
| **VII. Port Binding** | ✅ | Chaque service expose son propre port |
| **VIII. Concurrency** | ⚠️ | ETL single-process, scalable via Docker replicas |
| **IX. Disposability** | ✅ | Healthchecks, graceful shutdown, entrypoints configurés |
| **X. Dev/Prod Parity** | ✅ | Docker garantit environnements identiques |
| **XI. Logs** | ⚠️ | Logs stdout/stderr, pas de centralisation externe |
| **XII. Admin Processes** | ✅ | Scripts run-init.sh, entrypoint.sh pour tâches admin |

**Score Global** : 8/12 (67%) ✅ Production-ready avec améliorations possibles

---

## 🐛 Troubleshooting

### Problème : Service ne démarre pas

**Solution** :
```powershell
# Vérifier les logs
docker-compose logs <service-name>

# Rebuild complet
docker-compose down
docker-compose up -d --build
```

### Problème : Healthcheck MySQL échoue

**Solution** :
```powershell
# Vérifier l'état
docker-compose ps

# Si mysql en "unhealthy" → attendre 30-60s
# Ou redémarrer MySQL
docker-compose restart mysql
```

### Problème : ETL ne trouve pas les données

**Symptômes** : Logs "SUCCESS: 0 records processed"

**Solution** :
1. Vérifier `DATASET_API_URL` dans `.env`
2. Tester l'API manuellement : `curl <DATASET_API_URL>`
3. Vérifier les logs ETL : `docker-compose logs etl`

### Problème : Streamlit affiche "Image non disponible"

**Solution** :
1. Vérifier que les images existent : `ls frontend/Dashboards/Executive/`
2. Rebuild Streamlit : `docker-compose up -d --build streamlit`
3. Vérifier les permissions des fichiers

### Problème : Superset ne se connecte pas à MySQL

**Solution** :
```powershell
# Vérifier les credentials dans .env
# Tester la connexion MySQL
docker exec -it <mysql-container> mysql -u admin -p

# Reconstruire Superset
docker-compose up -d --build superset
```

---

## 📝 Logging et Monitoring

### Format des Logs

**ETL** :
```
[2024-11-24 10:30:45] INFO: Starting ETL pipeline
[2024-11-24 10:30:50] INFO: STEP 1 - Extraction from API
[2024-11-24 10:31:20] SUCCESS: 1000 records extracted
[2024-11-24 10:31:25] INFO: STEP 2 - Transformation
[2024-11-24 10:31:40] SUCCESS: 1000 records transformed
[2024-11-24 10:31:45] INFO: STEP 3 - Loading to MySQL
[2024-11-24 10:32:10] SUCCESS: 1000 records loaded
```

**Streamlit** :
```
INFO: Application started on port 8501
INFO: Loading dashboard images...
SUCCESS: 11 images loaded successfully
```

### Healthchecks

Tous les services ont des healthchecks configurés :
- **MySQL** : `mysqladmin ping` toutes les 10s
- **Superset** : HTTP check sur port 8088
- **Streamlit** : `curl http://localhost:8501/_stcore/health`

---

## 🤝 Contribution

### Workflow de Développement

1. Créer une branche feature : `git checkout -b feature/ma-fonctionnalite`
2. Développer et tester localement avec Docker Compose
3. Committer avec messages descriptifs en français
4. Push et créer une Pull Request

### Standards de Code

- **Python** : PEP 8, docstrings en français
- **SQL** : Nommage en snake_case
- **Docker** : Multi-stage builds si possible
- **Logs** : Format professionnel, pas d'emojis

---

## 📚 Ressources

### Documentation Externe

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Apache Superset](https://superset.apache.org/docs/intro)
- [OpenData Paris API](https://opendata.paris.fr/explore/)
- [MySQL 8.0 Reference](https://dev.mysql.com/doc/refman/8.0/en/)
- [12-Factor App Methodology](https://12factor.net/)

### Contact & Support

- **Repository** : AlaDdin0709/immobilisations_amortissements
- **Branche** : restore-V3
- **Issues** : Utiliser GitHub Issues pour les bugs et demandes de fonctionnalités

---

## 📄 Licence

Ce projet est destiné à des fins éducatives et d'analyse de données publiques.

---

**Dernière mise à jour** : 24 novembre 2025  
**Version** : 1.0.0  
**Mainteneur** : AlaDdin0709
