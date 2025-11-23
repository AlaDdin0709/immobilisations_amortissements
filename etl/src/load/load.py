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
    user = os.getenv('MYSQL_USER', 'root')
    pw = os.getenv('MYSQL_PASSWORD', '')
    host = os.getenv('MYSQL_HOST', 'mysql')
    port = os.getenv('MYSQL_PORT', 3306)
    db = os.getenv('MYSQL_DATABASE')
    url = f'mysql+pymysql://{user}:{pw}@{host}:{port}/{db}'
    return create_engine(url, pool_pre_ping=True)


def upsert_immobilisations(df: pd.DataFrame, table_name: str = 'immobilisations_amortissements') -> int:
    """Upsert transformed immobilisations rows into the target table using SQLAlchemy ORM/table metadata.

    Notes:
    - The function uses MySQL's ON DUPLICATE KEY UPDATE via the MySQL dialect insert helper.
    - The loader expects the DataFrame to match the TARGET_SCHEMA columns (no `source_id` or `properties`).
    """
    engine = get_engine()
    conn = engine.connect()
    inserted = 0

    # prepare list of insertable/updatable columns from the ORM model (exclude PK autoinc and fetched_at)
    table = Immobilisation.__table__
    insert_cols = [c.name for c in table.columns if c.name not in ('id', 'fetched_at')]
    # columns to update on duplicate key (exclude primary identifier)
    update_cols = [c for c in insert_cols if c != 'ndeg_immobilisation']

    try:
        for row in df.to_dict(orient='records'):
            params = {col: row.get(col) for col in insert_cols}

            # sanitize NaN to None
            for k, v in list(params.items()):
                try:
                    if pd.isna(v):
                        params[k] = None
                except Exception:
                    pass

            stmt = mysql_insert(table).values(**params)

            # build update mapping: set column = VALUES(column)
            update_mapping = {col: stmt.inserted[col] for col in update_cols}

            upsert_stmt = stmt.on_duplicate_key_update(**update_mapping)

            conn.execute(upsert_stmt)
            inserted += 1

        # commit the connection (use Connection.commit())
        try:
            conn.commit()
        except Exception:
            # Some SQLAlchemy versions require using the transaction API; ignore if unavailable
            pass
    finally:
        conn.close()

    logger.info('Upserted %s rows into %s', inserted, table_name)
    return inserted
