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
    """Load transformed immobilisations rows into the target table in append-only mode.

    Behavior changes (compared to prior upsert):
    - Ensures the target table exists by running metadata.create_all()
    - Performs bulk INSERT (append) of rows; duplicates are allowed at the DB level
      (the unique constraint on `ndeg_immobilisation` was removed in the ORM model).

    This keeps the public API name `upsert_immobilisations` so callers (e.g., `main.py`)
    don't need to be changed.
    """
    engine = get_engine()
    conn = engine.connect()
    inserted = 0

    # ensure table exists according to ORM metadata
    try:
        Base.metadata.create_all(engine)
    except Exception:
        logger.exception('Failed to ensure target table exists')

    table = Immobilisation.__table__
    insert_cols = [c.name for c in table.columns if c.name not in ('id', 'fetched_at')]

    # Prepare rows for bulk insert
    records = []
    for row in df.to_dict(orient='records'):
        params = {col: row.get(col) for col in insert_cols}
        # sanitize NaN to None
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

    trans = conn.begin()
    try:
        # bulk insert using core table insert
        result = conn.execute(table.insert(), records)
        try:
            trans.commit()
        except Exception:
            # commit can be no-op for some engines; ignore
            pass
        # result.rowcount may be -1 for some drivers; use len(records) as best-effort
        inserted = len(records)
    except Exception:
        trans.rollback()
        logger.exception('Bulk insert failed')
        raise
    finally:
        conn.close()

    logger.info('Inserted %s rows into %s', inserted, table_name)
    return inserted
