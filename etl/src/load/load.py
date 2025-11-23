import os
import json
import logging
import pandas as pd
from sqlalchemy import create_engine, text
import uuid

logger = logging.getLogger(__name__)


def get_engine():
    user = os.getenv('MYSQL_USER', 'root')
    pw = os.getenv('MYSQL_PASSWORD', '')
    host = os.getenv('MYSQL_HOST', 'mysql')
    port = os.getenv('MYSQL_PORT', 3306)
    db = os.getenv('MYSQL_DATABASE')
    url = f'mysql+pymysql://{user}:{pw}@{host}:{port}/{db}'
    return create_engine(url, pool_pre_ping=True)


def upsert_immobilisations(df, table_name='immobilisations_amortissements'):
    """Upsert transformed immobilisations rows into the target table.

    Expects DataFrame with columns matching the TARGET_SCHEMA keys and `source_id` and `properties`.
    """
    engine = get_engine()
    conn = engine.connect()
    inserted = 0

    # Use a concise parameterized upsert statement. Columns list kept minimal and stable.
    stmt = text(
        """
        INSERT INTO immobilisations_amortissements (
            ndeg_immobilisation, publication, collectivite, nature, date_d_acquisition,
            designation_des_ensembles, valeur_d_acquisition, duree_amort,
            cumul_amort_anterieurs, vnc_debut_exercice, amort_exercice, vnc_fin_exercice,
            source_id, properties
        ) VALUES (
            :ndeg_immobilisation, :publication, :collectivite, :nature, :date_d_acquisition,
            :designation_des_ensembles, :valeur_d_acquisition, :duree_amort,
            :cumul_amort_anterieurs, :vnc_debut_exercice, :amort_exercice, :vnc_fin_exercice,
            :source_id, :properties
        )
        ON DUPLICATE KEY UPDATE
            publication=VALUES(publication), collectivite=VALUES(collectivite), nature=VALUES(nature),
            date_d_acquisition=VALUES(date_d_acquisition), designation_des_ensembles=VALUES(designation_des_ensembles),
            valeur_d_acquisition=VALUES(valeur_d_acquisition), duree_amort=VALUES(duree_amort),
            cumul_amort_anterieurs=VALUES(cumul_amort_anterieurs), vnc_debut_exercice=VALUES(vnc_debut_exercice),
            amort_exercice=VALUES(amort_exercice), vnc_fin_exercice=VALUES(vnc_fin_exercice), properties=VALUES(properties), fetched_at=CURRENT_TIMESTAMP
        """
    )

    try:
        # Iterate records and execute upsert. Keep logic simple and explicit.
        for row in df.to_dict(orient='records'):
            params = {}
            for col in [
                'ndeg_immobilisation', 'publication', 'collectivite', 'nature', 'date_d_acquisition',
                'designation_des_ensembles', 'valeur_d_acquisition', 'duree_amort', 'cumul_amort_anterieurs',
                'vnc_debut_exercice', 'amort_exercice', 'vnc_fin_exercice', 'source_id'
            ]:
                params[col] = row.get(col)

            # properties JSON
            params['properties'] = json.dumps(row.get('properties') or {}, ensure_ascii=False)

            # sanitize NaN to None
            for k, v in list(params.items()):
                try:
                    if pd.isna(v):
                        params[k] = None
                except Exception:
                    pass

            # ensure primary key exists; if not, generate a surrogate here as well
            if not params.get('ndeg_immobilisation'):
                params['ndeg_immobilisation'] = f"gen-{uuid.uuid4().hex}"
                params['source_id'] = params.get('source_id') or params['ndeg_immobilisation']

            conn.execute(stmt, params)
            inserted += 1
        conn.commit()
    finally:
        conn.close()

    logger.info('Upserted %s rows into %s', inserted, table_name)
    return inserted
