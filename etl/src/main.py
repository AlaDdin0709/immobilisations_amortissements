"""Pipeline ETL principal pour les données d'immobilisations.

Ce script orchestre l'extraction, la transformation et le chargement
des données depuis l'API OpenData Paris vers MySQL.
"""
import os
import logging
from extract.extract import fetch_records_in_batches
from config import BATCH_SIZE
from transform.transform import (
    transform_records,
    calculate_derived_fields,
    add_data_quality_flags,
)
from load.load import upsert_immobilisations

# Configuration du logging (niveau contrôlé par la variable LOG_LEVEL)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)


def run_etl():
    """
    Exécute le pipeline ETL complet :
    - Extraction depuis l'API OpenData Paris
    - Transformation et nettoyage des données
    - Chargement dans MySQL
    """
    logger.info("%s", "=" * 60)
    logger.info("Starting ETL Pipeline")
    logger.info("%s", "=" * 60)
    
    # ========================================
    # ÉTAPE 1: EXTRACTION
    # ========================================
    logger.info("\nSTEP 1: EXTRACTION")
    logger.info("-" * 60)
    
    # Extraction en streaming par lots pour gérer de gros volumes
    total_extracted = 0

    logger.info("Streaming extraction in batches (batch_size=%s)", BATCH_SIZE)
    
    # ========================================
    # ÉTAPE 2: TRANSFORMATION
    # ========================================
    logger.info("\nSTEP 2: TRANSFORMATION")
    logger.info("-" * 60)
    
    # Récupérer le nom de la table cible
    table_name = os.getenv('ETL_TABLE', 'immobilisations_amortissements')
    logger.info("Target table: %s", table_name)

    total_loaded = 0
    total_transformed = 0

    # Traiter chaque lot d'enregistrements
    for batch in fetch_records_in_batches(rows=BATCH_SIZE):
        total_extracted += len(batch)
        logger.info("Processing batch: %s records", f"{len(batch):,}")

        # Transformer les données brutes en DataFrame structuré
        df = transform_records(batch)
        
        # Calculer les champs dérivés (taux, âge, etc.)
        df = calculate_derived_fields(df)
        
        # Ajouter les indicateurs de qualité des données
        df = add_data_quality_flags(df)

        if df.empty:
            logger.warning("Batch produced no rows after transformation - skipping")
            continue
            
        # Compter les lignes transformées
        total_transformed += len(df)
        
        # Charger les données dans MySQL
        loaded = upsert_immobilisations(df, table_name=table_name)
        total_loaded += loaded
        logger.info("Batch loaded: %s rows", f"{loaded:,}")

    # Vérifier qu'au moins un enregistrement a été extrait
    if total_extracted == 0:
        logger.error("ERROR: No records fetched - Aborting ETL")
        return

    # Résumé final du pipeline
    logger.info("SUCCESS: Extraction/Loading completed: %s records extracted, %s rows transformed, %s rows loaded", f"{total_extracted:,}", f"{total_transformed:,}", f"{total_loaded:,}")


if __name__ == '__main__':
    try:
        run_etl()
        logger.info("\nETL process exited cleanly")
        exit(0)
    except Exception as e:
        logger.exception("\nFATAL ERROR: %s", e)
        exit(1)
