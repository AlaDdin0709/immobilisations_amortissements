"""Fonctions utilitaires pour la conversion de types de données.

Ce module fournit des fonctions robustes pour convertir les valeurs
en types appropriés (date, int, decimal, string, text).
"""
from typing import Any, Optional
import datetime
import pandas as pd

# ============================================================================
# FONCTIONS DE CONVERSION DE TYPES
# ============================================================================

def to_date(value: Any) -> Optional[datetime.date]:
    """
    Convertit une valeur en date, gère plusieurs formats.
    
    Args:
        value: Valeur à convertir (string, datetime, date, etc.)
        
    Returns:
        datetime.date ou None si conversion impossible
    """
    if value in (None, '') or pd.isna(value):
        return None
    
    # Si déjà une date ou datetime, normaliser en date
    if isinstance(value, datetime.date):
        # datetime.date est la classe parente de datetime.datetime
        if isinstance(value, datetime.datetime):
            return value.date()
        return value

    try:
        # Essayer le format ISO d'abord (YYYY-MM-DD)
        return datetime.datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
    except (ValueError, TypeError):
        pass
    
    # Essayer des formats additionnels
    for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']:
        try:
            return datetime.datetime.strptime(str(value), fmt).date()
        except (ValueError, TypeError):
            continue
    
    return None


def to_int(value: Any) -> Optional[int]:
    """
    Convertit une valeur en entier, gère les valeurs manquantes.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        int ou None si conversion impossible
    """
    if value in (None, '') or pd.isna(value):
        return None
    
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def to_decimal(value: Any) -> Optional[float]:
    """
    Convertit une valeur en décimal/float, gère les valeurs manquantes.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        float ou None si conversion impossible
    """
    if value in (None, '') or pd.isna(value):
        return None
    
    try:
        # Gérer les nombres avec virgules ou espaces
        if isinstance(value, str):
            value = value.replace(',', '.').replace(' ', '')
        return float(value)
    except (ValueError, TypeError):
        return None


def to_string(value: Any) -> Optional[str]:
    """
    Convertit une valeur en chaîne, normalise les espaces.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        str ou None si valeur vide
    """
    if value is None or pd.isna(value):
        return None
    
    result = str(value).strip()
    return result if result else None


def to_text(value: Any) -> Optional[str]:
    """
    Convertit une valeur en texte, préserve le formatage.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        str ou None si valeur vide
    """
    if value is None or pd.isna(value):
        return None
    
    result = str(value)
    # Normaliser l'unicode et supprimer les espaces excessifs
    result = ' '.join(result.split())
    return result if result else None