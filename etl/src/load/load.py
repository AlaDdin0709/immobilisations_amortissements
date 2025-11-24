"""
Module de chargement des données dans la base MySQL.

Ce module insère les données transformées dans la table immobilisations_amortissements.
"""
import os
import json
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import insert as mysql_insert
from models import Immobilisation, Base

logger = logging.getLogger(__name__)


def get_engine():
    """
    Crée et retourne un moteur SQLAlchemy pour MySQL.
    
    Returns:
        Engine SQLAlchemy configuré avec les variables d'environnement
    """
    # Récupérer les paramètres de connexion depuis les variables d'environnement
    user = os.getenv('MYSQL_USER', 'root')
    pw = os.getenv('MYSQL_PASSWORD', '')
    host = os.getenv('MYSQL_HOST', 'mysql')
    port = os.getenv('MYSQL_PORT', 3306)
    db = os.getenv('MYSQL_DATABASE')
    
    # Construire l'URL de connexion
    url = f'mysql+pymysql://{user}:{pw}@{host}:{port}/{db}'
    
    # Créer le moteur avec pool_pre_ping pour gérer les connexions perdues
    return create_engine(url, pool_pre_ping=True)


def upsert_immobilisations(df: pd.DataFrame, table_name: str = 'immobilisations_amortissements') -> int:
    """
    Insère les données du DataFrame dans la table MySQL.
    
    Args:
        df: DataFrame contenant les données à insérer
        table_name: Nom de la table cible (défaut: immobilisations_amortissements)
        
    Returns:
        Nombre d'enregistrements insérés
    """
    engine = get_engine()
    conn = engine.connect()
    inserted = 0

    try:
        # Créer les tables si elles n'existent pas
        Base.metadata.create_all(engine)
    except Exception:
        logger.exception('Failed to ensure target table exists')

    # Récupérer la définition de la table
    table = Immobilisation.__table__
    
    # Colonnes à insérer (exclure id et fetched_at qui sont auto-générés)
    insert_cols = [c.name for c in table.columns if c.name not in ('id', 'fetched_at')]

    # Préparer les enregistrements pour l'insertion
    records = []
    for row in df.to_dict(orient='records'):
        # Extraire les valeurs des colonnes à insérer
        params = {col: row.get(col) for col in insert_cols}
        
        # Nettoyer les valeurs NaN (remplacer par None pour SQL NULL)
        for k, v in list(params.items()):
            try:
                if pd.isna(v):
                    params[k] = None
            except Exception:
                pass
        records.append(params)

    if not records:
        logger.info('No records to insert into %s', table_name)
        return 0

    # Démarrer une transaction
    trans = conn.begin()
    try:
        # Insérer tous les enregistrements
        result = conn.execute(table.insert(), records)
        try:
            trans.commit()
        except Exception:
            pass
        inserted = len(records)
    except Exception:
        # En cas d'erreur, annuler la transaction
        trans.rollback()
        logger.exception('Bulk insert failed')
        raise
    finally:
        conn.close()

    logger.info('Inserted %s rows into %s', inserted, table_name)
    return inserted
