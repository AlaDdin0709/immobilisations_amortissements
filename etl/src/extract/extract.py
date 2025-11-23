import os
import requests
import time
import logging
from dotenv import load_dotenv

load_dotenv()

DATASET_ID = "immobilisations-etat-des-amortissements"

logger = logging.getLogger(__name__)


API_URL = os.getenv('DATASET_API_URL')


def fetch_all_records():
    """
    Extraction paginée via Opendatasoft API (limite de 10 000 résultats).
    Arrête proprement si la limite est atteinte (400 error).
    """
    logger.info("🚀 Démarrage de l'extraction par pagination (offset/rows)...")

    base_url = "https://opendata.paris.fr"
    search_url = f"{base_url}/api/records/1.0/search"

    all_records = []
    start = 0
    rows = 1000  # chunk/page size
    max_retries = 3
    backoff = 2

    while True:
        params = {
            'dataset': DATASET_ID,
            'rows': rows,
            'start': start
        }
        attempt = 0
        while attempt < max_retries:
            try:
                logger.debug('Requesting page start=%s rows=%s', start, rows)
                resp = requests.get(search_url, params=params, timeout=120)
                resp.raise_for_status()
                payload = resp.json()
                break
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 400:
                    logger.warning(f"400 error pour start={start}, extraction stoppée (limite API atteinte).")
                    logger.info('✅ Records extraits (limite atteinte): %s', f"{len(all_records):,}")
                    return all_records
                else:
                    attempt += 1
                    logger.warning('Request failed (attempt %s/%s): %s', attempt, max_retries, e)
                    time.sleep(backoff * attempt)
        else:
            logger.error('❌ Plusieurs tentatives échouées pour start=%s', start)
            logger.info('✅ Records extraits (avant erreur): %s', f"{len(all_records):,}")
            return all_records

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
            break

        # append and advance
        all_records.extend(records)

        # If we received fewer than requested rows, we're done
        if len(records) < rows:
            break

        start += rows

    logger.info('✅ Pagination terminée: total records=%s', f"{len(all_records):,}")
    return all_records



if __name__ == '__main__':
    logger.info("🧪 Test d'extraction")
    records = fetch_all_records()
    logger.info("✅ Total récupéré: %s enregistrements", f"{len(records):,}")
    
    if records:
        logger.info("\n📋 Exemple de record:")
        logger.info(records[0])
