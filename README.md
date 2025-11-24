# Plateforme d'Analyse des Immobilisations et Amortissements

## Table des Matières

1. [Introduction](#introduction)
2. [Structure du Projet](#structure-du-projet)
3. [Services Docker Compose](#services-docker-compose)
4. [Stack Technique](#stack-technique)
5. [Pipeline ETL Détaillé](#pipeline-etl-détaillé)
6. [Interface Streamlit](#interface-streamlit)
7. [Installation et Démarrage](#installation-et-démarrage)
8. [Accès aux Services](#accès-aux-services)
9. [Conformité 12-Factor App](#conformité-12-factor-app)
10. [Ressources](#ressources)

---

## Introduction

Cette plateforme d'analyse automatisée permet la visualisation et le suivi des immobilisations et amortissements à partir des données OpenData Paris. Le système extrait, transforme et charge (ETL) automatiquement les données publiques, puis les présente via une interface Streamlit intuitive avec des tableaux de bord interactifs générés automatiquement dans Apache Superset. Les dashboards Superset sont importés et configurés de manière automatique au démarrage, offrant des visualisations interactives accessibles directement depuis l'interface web.

### Objectifs du Projet

- **Automatisation complète** : Pipeline ETL autonome pour la collecte et le traitement des données
- **Visualisation moderne** : Interface Streamlit avec dashboards statiques exportés depuis Superset
- **Architecture cloud-ready** : Conformité aux principes 12-Factor App
- **Production-ready** : Containerisation Docker, healthchecks, logging professionnel

### Fonctionnalités Principales

- **ETL Automatisé** : Extraction par batch depuis l'API OpenData Paris (1000 enregistrements/batch)  
- **Transformation Avancée** : Calcul automatique des champs dérivés (taux d'amortissement, âge, valeur restante)  
- **Base de Données MySQL** : Stockage optimisé avec indexes et contraintes  
- **Dashboards Superset** : Visualisations avancées (acquisitions, répartitions, analyses temporelles)  
- **Interface Streamlit** : Navigation intuitive avec 3 pages (Accueil, Vue Executive, Analyse Temporelle)  
- **Mode Statique** : Affichage des dashboards via images JPG (pas de requêtes SQL en temps réel)

---

## Structure du Projet

```
immobilisations_amortissements/
│
├── docker-compose.yml          # Orchestration des services
├── .env.example                # Template de configuration
├── .gitignore                  # Fichiers exclus du versioning
├── README.md                   # Documentation (ce fichier)
│
├── etl/                        # Pipeline ETL
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
├── mysql/                      # Base de Données
│   ├── init.sql                # Schéma et initialisation
│   └── run-init.sh             # Script d'initialisation
│
├── superset/                   # Business Intelligence
│   ├── Dockerfile              # Image Superset personnalisée
│   ├── superset_config.py      # Configuration Superset
│   ├── init-superset.sh        # Initialisation automatique
│   └── dashboards/             # Exports des dashboards
│       ├── dashboard_executive.json
│       └── dashboard_temporel.json
│
├── frontend/                   # Interface Utilisateur
│   ├── Dockerfile              # Image Streamlit
│   ├── requirements.txt        # Dépendances légères
│   ├── Home.py                 # Page d'accueil
│   ├── pages/
│   │   ├── 1_Vue_Executive.py
│   │   └── 2_Analyse_Temporelle.py
│   └── Dashboards/             # Images statiques des dashboards
│       ├── nombre-total-d-actifs.jpg
│       ├── totale-d-acquisition-par-annee.jpg
│       ├── repartition-par-nature.jpg
│       ├── top-10-immobilisations-par-valeur.jpg
│       ├── valleur-dacquisition-par-collectivite.jpg
│       ├── acquisitions-par-annee.jpg
│       ├── acquisitions-par-trimestre.jpg
│       ├── nombre-dacquisitions-par-mois-annee.jpg
│       ├── amortissement-cumule.jpg
│       ├── VUE EXÉCUTIVE dashboard.jpg
│       └── ANALYSE TEMPORELLE dashboard.jpg
│
└── notebooks/                  # Jupyter notebooks (analyse ad-hoc)
```

---

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
- **Git** : Contrôle de version

---

## Pipeline ETL Détaillé

### 1. Extraction

**Source** : API OpenData Paris  
**Méthode** : Pagination automatique avec générateur Python  
**Batch Size** : 1000 enregistrements par requête  
**Gestion d'erreurs** : Retry sur timeout, fallback pour réponses liste

### 2. Transformation

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

### 3. Chargement

**Stratégie** : UPSERT (INSERT ... ON DUPLICATE KEY UPDATE)  
**Transaction** : Rollback automatique en cas d'erreur  
**Performance** : Bulk insert avec SQLAlchemy  
**Sanitization** : Conversion NaN/Infinity avant insertion

---

## Interface Streamlit

### Architecture Multi-Pages

#### Page d'Accueil (`Home.py`)
- **Statistiques** : Compteurs d'images par dashboard
- **Navigation** : Cards cliquables vers les dashboards

#### Vue Executive (`1_Vue_Executive.py`)
- **Mode 1** : Dashboard complet (image unique)
- **Mode 2** : Graphiques détaillés en onglets
  - Nombre Total d'Actifs
  - Totale d'Acquisition par Année
  - Répartition par Nature
  - Top 10 Immobilisations par Valeur
  - Valeur d'Acquisition par Collectivité
- **Fonctionnalités** : Téléchargement individuel des images

#### Analyse Temporelle (`2_Analyse_Temporelle.py`)
- **Mode 1** : Dashboard temporel complet
- **Mode 2** : Analyses détaillées
  - Acquisitions par Année
  - Acquisitions par Trimestre
  - Nombre d'Acquisitions par Mois/Année
  - Amortissement Cumulé

---

## Installation et Démarrage

### Prérequis

- **Docker** : Version 20.10+
- **Docker Compose** : Version 2.0+
- **Git** : Pour cloner le repository
- **Ports disponibles** : 3306 (MySQL), 8080 (Adminer), 8088 (Superset), 8501 (Streamlit)

### Configuration Initiale

**1. Cloner le repository**
```powershell
git clone https://github.com/AlaDdin0709/immobilisations_amortissements.git
cd immobilisations_amortissements
```

**2. Configurer les variables d'environnement**
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

**3. Lancer la plateforme**
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

| Service | URL |
|---------|-----|
| **Streamlit** | http://localhost:8501 |
| **Superset** | http://localhost:8088 |
| **Adminer** | http://localhost:8080 |
| **MySQL** | localhost:3306 |

---

## Conformité 12-Factor App

| Facteur | Statut | Implémentation |
|---------|--------|----------------|
| **I. Codebase** | OUI | Repository Git unique, branche `restore-V3` |
| **II. Dependencies** | OUI | `requirements.txt` pour Python, images Docker versionnées |
| **III. Config** | OUI | Variables d'environnement via `.env` (12-factor compliant) |
| **IV. Backing Services** | OUI | MySQL, Superset traités comme ressources attachables |
| **V. Build/Release/Run** | OUI | Docker build → Docker Compose up (séparation stricte) |
| **VI. Processes** | OUI | Services stateless, état en base MySQL |
| **VII. Port Binding** | OUI | Chaque service expose son propre port |
| **VIII. Concurrency** | OUI | ETL single-process, scalable via Docker replicas |
| **IX. Disposability** | OUI | Healthchecks, graceful shutdown, entrypoints configurés |
| **X. Dev/Prod Parity** | OUI | Docker garantit environnements identiques |
| **XI. Logs** | OUI | Logs stdout/stderr, pas de centralisation externe |
| **XII. Admin Processes** | OUI | Scripts run-init.sh, entrypoint.sh pour tâches admin |

---

## Ressources

### Documentation Externe

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Apache Superset](https://superset.apache.org/docs/intro)
- [OpenData Paris API](https://opendata.paris.fr/explore/)
- [MySQL 8.0 Reference](https://dev.mysql.com/doc/refman/8.0/en/)
- [12-Factor App Methodology](https://12factor.net/)

### Contact & Support

- **Repository** : AlaDdin0709/immobilisations_amortissements
- **Issues** : Utiliser GitHub Issues pour les bugs et demandes de fonctionnalités

---

## Licence

Ce projet est destiné à des fins éducatives et d'analyse de données publiques.

---

**Version** : 1.0.0  
**Mainteneur** : AlaDdin0709
