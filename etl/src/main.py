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

# Logging configuration (controlled via LOG_LEVEL env)
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
    
    # Stream extraction in batches; process each batch immediately.
    total_extracted = 0

    logger.info("Streaming extraction in batches (batch_size=%s)", BATCH_SIZE)
    
    # ========================================
    # ÉTAPE 2: TRANSFORMATION
    # ========================================
    logger.info("\nSTEP 2: TRANSFORMATION")
    logger.info("-" * 60)
    
    table_name = os.getenv('ETL_TABLE', 'immobilisations_amortissements')
    logger.info("Target table: %s", table_name)

    total_loaded = 0
    total_transformed = 0

    for batch in fetch_records_in_batches(rows=BATCH_SIZE):
        total_extracted += len(batch)
        logger.info("Processing batch: %s records", f"{len(batch):,}")

        df = transform_records(batch)
        df = calculate_derived_fields(df)
        df = add_data_quality_flags(df)

        if df.empty:
            logger.warning("Batch produced no rows after transformation - skipping")
            continue
        # count transformed rows and load
        total_transformed += len(df)
        loaded = upsert_immobilisations(df, table_name=table_name)
        total_loaded += loaded
        logger.info("Batch loaded: %s rows", f"{loaded:,}")

    if total_extracted == 0:
        logger.error("ERROR: No records fetched - Aborting ETL")
        return

    logger.info("SUCCESS: Extraction/Loading completed: %s records extracted, %s rows transformed, %s rows loaded", f"{total_extracted:,}", f"{total_transformed:,}", f"{total_loaded:,}")

if __name__ == '__main__':
    try:
        run_etl()
        logger.info("\nETL process exited cleanly")
        exit(0)
    except Exception as e:
        logger.exception("\nFATAL ERROR: %s", e)
        exit(1)
