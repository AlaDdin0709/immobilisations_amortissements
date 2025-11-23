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