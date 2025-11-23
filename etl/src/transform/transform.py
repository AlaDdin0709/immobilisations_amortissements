import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

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
# TYPE CONVERSION FUNCTIONS
# ============================================================================

def to_date(value: Any) -> Optional[datetime.date]:
    """Convert value to date, handling various formats."""
    if value in (None, '') or pd.isna(value):
        return None
    
    if isinstance(value, datetime):
        return value.date()
    
    try:
        # Try ISO format first
        return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
    except (ValueError, TypeError):
        pass
    
    # Try additional formats
    for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']:
        try:
            return datetime.strptime(str(value), fmt).date()
        except (ValueError, TypeError):
            continue
    
    return None


def to_int(value: Any) -> Optional[int]:
    """Convert value to integer, handling missing values."""
    if value in (None, '') or pd.isna(value):
        return None
    
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def to_decimal(value: Any) -> Optional[float]:
    """Convert value to decimal/float, handling missing values."""
    if value in (None, '') or pd.isna(value):
        return None
    
    try:
        # Handle string numbers with commas or spaces
        if isinstance(value, str):
            value = value.replace(',', '.').replace(' ', '')
        return float(value)
    except (ValueError, TypeError):
        return None


def to_string(value: Any) -> Optional[str]:
    """Convert value to string, normalizing whitespace."""
    if value is None or pd.isna(value):
        return None
    
    result = str(value).strip()
    return result if result else None


def to_text(value: Any) -> Optional[str]:
    """Convert value to text, preserving formatting."""
    if value is None or pd.isna(value):
        return None
    
    result = str(value)
    # Normalize unicode and remove excessive whitespace
    result = ' '.join(result.split())
    return result if result else None


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

def extract_fields(record: Any) -> Dict[str, Any]:
    """Extract fields from various record formats."""
    if not isinstance(record, dict):
        return {}
    
    # Handle nested 'fields' structure
    if 'fields' in record and isinstance(record.get('fields'), dict):
        return record['fields']
    
    # Return the record itself if it's already flat
    return record


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
    pk_candidates = [
        fields.get('ndeg_immobilisation'),
        fields.get('NDEG_IMMOBILISATION'),
        record.get('recordid'),
        record.get('id'),
        record.get('source_id'),
    ]
    
    for candidate in pk_candidates:
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
    extra_fields = {}
    
    # Apply type conversions for schema fields
    for column, data_type in target_schema.items():
        value = fields.get(column)
        converter = TYPE_CONVERTERS.get(data_type, to_string)
        transformed_row[column] = converter(value)
    
    # Collect extra fields not in schema
    for key, value in fields.items():
        if key not in target_schema:
            extra_fields[key] = value
    
    # Handle primary key
    source_id = extract_primary_key(record if isinstance(record, dict) else {}, fields)
    transformed_row['ndeg_immobilisation'] = transformed_row.get('ndeg_immobilisation') or source_id
    
    # Add metadata
    transformed_row['source_id'] = source_id
    transformed_row['properties'] = extra_fields if extra_fields else {}
    
    if isinstance(record, dict):
        transformed_row['record_timestamp'] = record.get('record_timestamp')
    
    return transformed_row


# ============================================================================
# BATCH TRANSFORMATION WITH REPORTING
# ============================================================================

def transform_records(
    records_list: List[Any],
    target_schema: Dict[str, str] = TARGET_SCHEMA,
    normalize_names: bool = True
) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Transform a list of records into a DataFrame with detailed reporting.
    
    Args:
        records_list: List of records to transform
        target_schema: Schema definition with column names and types
        normalize_names: Whether to normalize field names
        
    Returns:
        Tuple of (DataFrame, report_dict)
    """
    rows = []
    report = {
        'total': len(records_list),
        'converted': 0,
        'errors': 0,
        'missing_fields': {},
        'null_primary_keys': 0,
    }
    
    for idx, record in enumerate(records_list):
        try:
            transformed = transform_single_record(record, target_schema, normalize_names)
            rows.append(transformed)
            
            # Track missing fields
            for column in target_schema.keys():
                if transformed.get(column) is None:
                    report['missing_fields'].setdefault(column, 0)
                    report['missing_fields'][column] += 1
            
        except Exception as e:
            report['errors'] += 1
            print(f"Error processing record {idx}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    report['converted'] = len(df)
    
    # Ensure column order matches schema
    column_order = list(target_schema.keys()) + ['source_id', 'properties', 'record_timestamp']
    df = df.reindex(columns=column_order)
    
    return df, report


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
    
    # Validate VNC consistency
    if all(col in df.columns for col in ['vnc_debut_exercice', 'amort_exercice', 'vnc_fin_exercice']):
        df['vnc_consistent'] = df.apply(
            lambda row: abs((row['vnc_debut_exercice'] or 0) - (row['amort_exercice'] or 0) - (row['vnc_fin_exercice'] or 0)) < 0.01
            if all(pd.notna([row['vnc_debut_exercice'], row['amort_exercice'], row['vnc_fin_exercice']])) else None,
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


def export_report(report: Dict[str, Any], output_path: str = 'transformation_report.json'):
    """Export transformation report to JSON file."""
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Report exported to {output_path}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Sample data
    sample_records = [
        {
            'fields': {
                'ndeg_immobilisation': 'IMM001',
                'publication': 'PUB2024',
                'date_d_acquisition': '2024-01-15',
                'valeur_d_acquisition': '50000.50',
                'duree_amort': '10',
            }
        },
        {
            'fields': {
                'ndeg_immobilisation': 'IMM002',
                'valeur_d_acquisition': '75000',
            }
        }
    ]
    
    # Transform records
    df, report = transform_records(sample_records)
    
    # Apply additional transformations
    df = calculate_derived_fields(df)
    df = add_data_quality_flags(df)
    
    print("Transformation Report:")
    print(f"Total records: {report['total']}")
    print(f"Converted: {report['converted']}")
    print(f"Errors: {report['errors']}")
    print(f"\nMissing fields: {report['missing_fields']}")
    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nFirst few rows:\n{df.head()}")