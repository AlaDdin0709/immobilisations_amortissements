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
# PRIMARY KEY GENERATION
# ============================================================================

def extract_primary_key(record: Dict[str, Any], fields: Dict[str, Any]) -> str:
    """Extract or generate a primary key for the record."""
    # Priority order for primary key selection
    candidate = fields.get('ndeg_immobilisation')
    if candidate and str(candidate).strip():
        return str(candidate).strip()

    # Generate UUID if no valid key found
    return f"gen-{uuid.uuid4().hex}"


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
    
    
    # Ensure primary key exists; generate inline if missing
    transformed_row['ndeg_immobilisation'] = transformed_row.get('ndeg_immobilisation') or f"gen-{uuid.uuid4().hex}"

    return transformed_row


# ============================================================================
# BATCH TRANSFORMATION WITH REPORTING
# ============================================================================

def transform_records(
    records_list: List[Any],
    target_schema: Dict[str, str] = TARGET_SCHEMA,
    normalize_names: bool = True
) -> pd.DataFrame:
    """
    Transform a list of records into a DataFrame.

    Args:
        records_list: List of records to transform
        target_schema: Schema definition with column names and types
        normalize_names: Whether to normalize field names

    Returns:
        pandas.DataFrame with transformed rows
    """
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
    
    # Calculate depreciation rate if duration is available
    if 'duree_amort' in df.columns and 'valeur_d_acquisition' in df.columns:
        df['taux_amortissement'] = df.apply(
            lambda row: (1 / row['duree_amort']) if row['duree_amort'] and row['duree_amort'] > 0 else None,
            axis=1
        )
    
    return df


def add_data_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add data quality indicator columns."""
    df = df.copy()
    
    # Flag records with missing critical fields
    critical_fields = ['ndeg_immobilisation', 'date_d_acquisition', 'valeur_d_acquisition']
    df['is_complete'] = df[critical_fields].notna().all(axis=1)
    
    # Flag potential duplicates
    if 'ndeg_immobilisation' in df.columns:
        df['is_duplicate'] = df.duplicated(subset=['ndeg_immobilisation'], keep=False)
    
    return df



