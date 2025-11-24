import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from utils.process import to_date, to_decimal, to_int, to_string, to_text

# TARGET_SCHEMA defines the expected columns and their types for schema-on-write.
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
# TYPE CONVERTER REGISTRY
# ============================================================================

TYPE_CONVERTERS: Dict[str, Callable] = {
    'date': to_date,
    'int': to_int,
    'decimal': to_decimal,
    'float': to_decimal,
    'string': to_string,
    'text': to_text,
}


# ============================================================================
# FIELD EXTRACTION AND NORMALIZATION
# ============================================================================

# field baz mawjoud fi record
def extract_fields(record: Any) -> Dict[str, Any]:
    """Extract fields from record, assuming 'fields' key always exists."""
    if isinstance(record, dict):
        return record['fields']  # expected to be present and a dict
    return {}


def normalize_field_names(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize field names to lowercase with underscores."""
    normalized = {}
    for key, value in fields.items():
        # Convert to lowercase and replace spaces with underscores
        normalized_key = key.lower().replace(' ', '_').replace('-', '_')
        normalized[normalized_key] = value
    return normalized

# ============================================================================
# RECORD TRANSFORMATION
# ============================================================================

def transform_single_record(
    record: Any,
    target_schema: Dict[str, str],
    normalize_names: bool = True
) -> Dict[str, Any]:
    """Transform a single record according to the target schema."""
    fields = extract_fields(record)
    
    if normalize_names:
        fields = normalize_field_names(fields)
    
    transformed_row = {}
    
    # Apply type conversions for schema fields
    for column, data_type in target_schema.items():
        value = fields.get(column)
        converter = TYPE_CONVERTERS.get(data_type, to_string)
        transformed_row[column] = converter(value)
    
    return transformed_row


# ============================================================================
# BATCH TRANSFORMATION WITH REPORTING
# ============================================================================

def transform_records(
    records_list: List[Any],
    target_schema: Dict[str, str] = TARGET_SCHEMA,
    normalize_names: bool = True
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for idx, record in enumerate(records_list):
        try:
            transformed = transform_single_record(record, target_schema, normalize_names)
            rows.append(transformed)
        except Exception as e:
            # Log the error and continue; do not raise to allow batch processing
            print(f"Error processing record {idx}: {e}")

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Ensure column order matches schema (keep only target schema columns)
    column_order = list(target_schema.keys())
    df = df.reindex(columns=column_order)

    return df


# ============================================================================
# ADDITIONAL TRANSFORMATIONS
# ============================================================================

def calculate_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate derived fields based on existing columns."""
    df = df.copy()
    
    # ========================================================================
    # 1. DEPRECIATION RATE
    # ========================================================================
    if 'duree_amort' in df.columns and 'valeur_d_acquisition' in df.columns:
        df['taux_amortissement'] = df.apply(
            lambda row: (1 / row['duree_amort']) if row['duree_amort'] and row['duree_amort'] > 0 else None,
            axis=1
        )
    
    # ========================================================================
    # 2. DATE COMPONENTS (Year, Month, Day, Quarter)
    # ========================================================================
    if 'date_d_acquisition' in df.columns:
        # Convert to datetime if not already
        df['date_d_acquisition'] = pd.to_datetime(df['date_d_acquisition'], errors='coerce')
        
        # Extract date components
        df['annee_acquisition'] = df['date_d_acquisition'].dt.year
        df['mois_acquisition'] = df['date_d_acquisition'].dt.month
        df['jour_acquisition'] = df['date_d_acquisition'].dt.day
        df['trimestre_acquisition'] = df['date_d_acquisition'].dt.quarter
    
    # ========================================================================
    # 3. ASSET AGE (in years)
    # ========================================================================
    if 'date_d_acquisition' in df.columns:
        today = pd.Timestamp.now()
        df['age_immobilisation'] = ((today - df['date_d_acquisition']).dt.days / 365.25).round(2)
    
    # ========================================================================
    # 4. TOTAL DEPRECIATION
    # ========================================================================
    if 'cumul_amort_anterieurs' in df.columns and 'amort_exercice' in df.columns:
        df['amortissement_total'] = (
            df['cumul_amort_anterieurs'].fillna(0) + 
            df['amort_exercice'].fillna(0)
        )
    
    # ========================================================================
    # 5. REMAINING VALUE PERCENTAGE
    # ========================================================================
    if 'vnc_fin_exercice' in df.columns and 'valeur_d_acquisition' in df.columns:
        df['pct_valeur_restante'] = (
            (df['vnc_fin_exercice'] / df['valeur_d_acquisition'] * 100)
            .where(df['valeur_d_acquisition'] > 0, None)
            .round(2)
        )
    
    return df


def add_data_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add data quality indicator columns."""
    df = df.copy()
    
    critical_fields = ['ndeg_immobilisation', 'date_d_acquisition', 'valeur_d_acquisition']
    df['_is_complete'] = df[critical_fields].notna().all(axis=1)
    
    # Potential duplicate check (kept as an in-memory indicator)
    if 'ndeg_immobilisation' in df.columns:
        df['_is_duplicate'] = df.duplicated(subset=['ndeg_immobilisation'], keep=False)
    
    # remove in-memory-only flags before returning to prevent persistence
    df = df.drop(columns=[c for c in ['_is_complete', '_is_duplicate'] if c in df.columns])
    return df