import os
import requests
import time
import logging
from config import DATASET_ID, SEARCH_URL

logger = logging.getLogger(__name__)


API_URL = os.getenv('DATASET_API_URL')


def fetch_records_in_batches(rows: int = 1000):
    """Generator that yields pages of records as they are fetched.

    This allows the ETL to transform & load batches incrementally instead of
    waiting for the full extraction to finish.
    """
    logger.info("🚀 Démarrage de l'extraction par pagination (streaming par batches)...")

    start = 0

    while True:
        params = {
            'dataset': DATASET_ID,
            'rows': rows,
            'start': start
        }

        try:
            logger.debug('Requesting page start=%s rows=%s', start, rows)
            resp = requests.get(SEARCH_URL, params=params, timeout=120)
            resp.raise_for_status()
            payload = resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 400:
                logger.warning(f"400 error pour start={start}, extraction stoppée (limite API atteinte).")
                return
            logger.error('Request failed for start=%s: %s', start, e)
            return

        # payload expected to have 'records' list
        records = []
        if isinstance(payload, dict) and 'records' in payload:
            records = payload.get('records', [])
        elif isinstance(payload, list):
            # fallback: some endpoints may return list
            records = payload
        else:
            logger.warning('⚠️ Format inattendu pour la page: %s', type(payload))

        logger.info('Page start=%s returned %s records', start, len(records))

        if not records:
            # no more records
            return

        yield records

        # If we received fewer than requested rows, we're done
        if len(records) < rows:
            return

        start += rows
