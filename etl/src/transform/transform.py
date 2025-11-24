"""Module de transformation des données d'immobilisations.

Ce module transforme les données brutes de l'API OpenData Paris
vers un format structuré pour la base de données.
"""
import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from utils.process import to_date, to_decimal, to_int, to_string, to_text

# Définition du schéma cible : colonnes attendues et leurs types
TARGET_SCHEMA: Dict[str, str] = {
    'ndeg_immobilisation': 'string',
    'publication': 'string',
    'collectivite': 'string',
    'nature': 'string',
    'date_d_acquisition': 'date',
    'designation_des_ensembles': 'text',
    'valeur_d_acquisition': 'decimal',
    'duree_amort': 'int',
    'cumul_amort_anterieurs': 'decimal',
    'vnc_debut_exercice': 'decimal',
    'amort_exercice': 'decimal',
    'vnc_fin_exercice': 'decimal',
}

# ============================================================================
# REGISTRE DES CONVERTISSEURS DE TYPES
# ============================================================================

# Dictionnaire associant chaque type de données à sa fonction de conversion
TYPE_CONVERTERS: Dict[str, Callable] = {
    'date': to_date,
    'int': to_int,
    'decimal': to_decimal,
    'float': to_decimal,
    'string': to_string,
    'text': to_text,
}


# ============================================================================
# EXTRACTION ET NORMALISATION DES CHAMPS
# ============================================================================

def extract_fields(record: Any) -> Dict[str, Any]:
    """Extrait les champs d'un enregistrement (clé 'fields')."""
    if isinstance(record, dict):
        return record['fields']  # Toujours présent dans les données OpenData
    return {}


def normalize_field_names(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise les noms de champs : minuscules avec underscores."""
    normalized = {}
    for key, value in fields.items():
        # Convertir en minuscules et remplacer espaces/tirets par underscores
        normalized_key = key.lower().replace(' ', '_').replace('-', '_')
        normalized[normalized_key] = value
    return normalized

# ============================================================================
# TRANSFORMATION D'ENREGISTREMENTS
# ============================================================================

def transform_single_record(
    record: Any,
    target_schema: Dict[str, str],
    normalize_names: bool = True
) -> Dict[str, Any]:
    """Transforme un enregistrement selon le schéma cible."""
    # Extraire les champs de l'enregistrement
    fields = extract_fields(record)
    
    # Normaliser les noms de champs si demandé
    if normalize_names:
        fields = normalize_field_names(fields)
    
    transformed_row = {}
    
    # Appliquer les conversions de type pour chaque colonne du schéma
    for column, data_type in target_schema.items():
        value = fields.get(column)
        converter = TYPE_CONVERTERS.get(data_type, to_string)
        transformed_row[column] = converter(value)
    
    return transformed_row


# ============================================================================
# TRANSFORMATION PAR LOT AVEC GESTION D'ERREURS
# ============================================================================

def transform_records(
    records_list: List[Any],
    target_schema: Dict[str, str] = TARGET_SCHEMA,
    normalize_names: bool = True
) -> pd.DataFrame:
    """Transforme une liste d'enregistrements en DataFrame."""
    rows: List[Dict[str, Any]] = []

    # Traiter chaque enregistrement
    for idx, record in enumerate(records_list):
        try:
            transformed = transform_single_record(record, target_schema, normalize_names)
            rows.append(transformed)
        except Exception as e:
            # Logger l'erreur et continuer le traitement du lot
            print(f"Erreur lors du traitement de l'enregistrement {idx}: {e}")

    # Créer le DataFrame
    df = pd.DataFrame(rows)

    # Assurer l'ordre des colonnes selon le schéma cible
    column_order = list(target_schema.keys())
    df = df.reindex(columns=column_order)

    return df


# ============================================================================
# TRANSFORMATIONS SUPPLÉMENTAIRES
# ============================================================================

def calculate_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule des champs dérivés à partir des colonnes existantes."""
    df = df.copy()
    
    # ========================================================================
    # 1. TAUX D'AMORTISSEMENT
    # ========================================================================
    if 'duree_amort' in df.columns and 'valeur_d_acquisition' in df.columns:
        df['taux_amortissement'] = df.apply(
            lambda row: (1 / row['duree_amort']) if row['duree_amort'] and row['duree_amort'] > 0 else None,
            axis=1
        )
    
    # ========================================================================
    # 2. COMPOSANTS DE DATE (Année, Mois, Jour, Trimestre)
    # ========================================================================
    if 'date_d_acquisition' in df.columns:
        # Convertir en datetime si nécessaire
        df['date_d_acquisition'] = pd.to_datetime(df['date_d_acquisition'], errors='coerce')
        
        # Extraire les composants de date
        df['annee_acquisition'] = df['date_d_acquisition'].dt.year
        df['mois_acquisition'] = df['date_d_acquisition'].dt.month
        df['jour_acquisition'] = df['date_d_acquisition'].dt.day
        df['trimestre_acquisition'] = df['date_d_acquisition'].dt.quarter
    
    # ========================================================================
    # 3. ÂGE DE L'IMMOBILISATION (en années)
    # ========================================================================
    if 'date_d_acquisition' in df.columns:
        today = pd.Timestamp.now()
        df['age_immobilisation'] = ((today - df['date_d_acquisition']).dt.days / 365.25).round(2)
    
    # ========================================================================
    # 4. AMORTISSEMENT TOTAL
    # ========================================================================
    if 'cumul_amort_anterieurs' in df.columns and 'amort_exercice' in df.columns:
        df['amortissement_total'] = (
            df['cumul_amort_anterieurs'].fillna(0) + 
            df['amort_exercice'].fillna(0)
        )
    
    # ========================================================================
    # 5. POURCENTAGE DE VALEUR RESTANTE
    # ========================================================================
    if 'vnc_fin_exercice' in df.columns and 'valeur_d_acquisition' in df.columns:
        df['pct_valeur_restante'] = (
            (df['vnc_fin_exercice'] / df['valeur_d_acquisition'] * 100)
            .where(df['valeur_d_acquisition'] > 0, None)
            .round(2)
        )
    
    return df


def add_data_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute des indicateurs de qualité des données."""
    df = df.copy()
    
    # Vérifier que les champs critiques sont présents
    critical_fields = ['ndeg_immobilisation', 'date_d_acquisition', 'valeur_d_acquisition']
    df['_is_complete'] = df[critical_fields].notna().all(axis=1)
    
    # Vérifier les doublons potentiels
    if 'ndeg_immobilisation' in df.columns:
        df['_is_duplicate'] = df.duplicated(subset=['ndeg_immobilisation'], keep=False)
    
    # Supprimer les flags temporaires pour éviter leur persistance
    df = df.drop(columns=[c for c in ['_is_complete', '_is_duplicate'] if c in df.columns])
    return df