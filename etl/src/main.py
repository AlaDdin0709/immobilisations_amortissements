import os
import logging
from extraction.extract import fetch_all_records
from transformation.transform import (
    transform_records,
    calculate_derived_fields,
    add_data_quality_flags,
)
from loading.load import upsert_immobilisations

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
    logger.info("🚀 Starting ETL Pipeline")
    logger.info("%s", "=" * 60)
    
    # ========================================
    # ÉTAPE 1: EXTRACTION
    # ========================================
    logger.info("\n📥 STEP 1: EXTRACTION")
    logger.info("-" * 60)
    
    records = fetch_all_records()
    
    if not records:
        logger.error("❌ No records fetched - Aborting ETL")
        return
    
    logger.info("✅ Extraction completed: %s records fetched", f"{len(records):,}")
    
    # ========================================
    # ÉTAPE 2: TRANSFORMATION
    # ========================================
    logger.info("\n🔄 STEP 2: TRANSFORMATION")
    logger.info("-" * 60)
    
    df, report = transform_records(records)
    logger.info("📊 Transform report: %s", report)
    
    # Apply derived fields and data quality flags (replacement for basic_cleaning)
    df = calculate_derived_fields(df)
    df = add_data_quality_flags(df)
    
    if df.empty:
        logger.error("❌ No data to load after transformation - Aborting ETL")
        return
    
    logger.info("✅ Transformation completed: %s rows, %s columns", f"{len(df):,}", len(df.columns))
    
    # ========================================
    # ÉTAPE 3: CHARGEMENT
    # ========================================
    logger.info("\n📤 STEP 3: LOADING TO MYSQL")
    logger.info("-" * 60)
    
    table_name = os.getenv('ETL_TABLE', 'immobilisations_amortissements')
    logger.info("Target table: %s", table_name)
    
    rows_loaded = upsert_immobilisations(df, table_name=table_name)
    
    logger.info("✅ Loading completed: %s rows upserted", f"{rows_loaded:,}")
    
    # ========================================
    # RÉSUMÉ
    # ========================================
    logger.info("\n%s", "=" * 60)
    logger.info("🎉 ETL PIPELINE FINISHED SUCCESSFULLY")
    logger.info("%s", "=" * 60)
    logger.info("📊 Summary:")
    logger.info("   - Records extracted   : %s", f"{len(records):,}")
    logger.info("   - Records transformed : %s", f"{len(df):,}")
    logger.info("   - Records loaded      : %s", f"{rows_loaded:,}")
    logger.info("   - Target table        : %s", table_name)
    logger.info("%s", "=" * 60)


if __name__ == '__main__':
    try:
        run_etl()
        logger.info("\n✅ ETL process exited cleanly")
        exit(0)
    except Exception as e:
        logger.exception("\n❌ FATAL ERROR: %s", e)
        exit(1)
