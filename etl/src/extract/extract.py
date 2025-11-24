"""Module d'extraction des données depuis l'API OpenData Paris.

Ce module récupère les données d'immobilisations par pagination
pour gérer de grands volumes de données efficacement.
"""
import os
import requests
import time
import logging
from config import DATASET_ID, SEARCH_URL

logger = logging.getLogger(__name__)

# URL de l'API (peut être surchargée par variable d'environnement)
API_URL = os.getenv('DATASET_API_URL')


def fetch_records_in_batches(rows: int = 1000):
    """
    Récupère les enregistrements par lots depuis l'API.
    
    Args:
        rows: Nombre d'enregistrements par page (défaut: 1000)
        
    Yields:
        Liste d'enregistrements pour chaque page
    """
    logger.info("Starting extraction by pagination (streaming by batches)...")

    start = 0  # Position de départ pour la pagination

    while True:
        # Paramètres de la requête API
        params = {
            'dataset': DATASET_ID,
            'rows': rows,
            'start': start
        }

        try:
            logger.debug('Requesting page start=%s rows=%s', start, rows)
            # Envoyer la requête avec un timeout de 120 secondes
            resp = requests.get(SEARCH_URL, params=params, timeout=120)
            resp.raise_for_status()
            payload = resp.json()
        except requests.exceptions.HTTPError as e:
            # Gérer l'erreur 400 (limite API atteinte)
            if e.response is not None and e.response.status_code == 400:
                logger.warning(f"400 error pour start={start}, extraction stoppée (limite API atteinte).")
                return
            logger.error('Request failed for start=%s: %s', start, e)
            return

        # Extraire les enregistrements de la réponse
        records = []
        if isinstance(payload, dict) and 'records' in payload:
            records = payload.get('records', [])
        elif isinstance(payload, list):
            # Fallback: certains endpoints retournent directement une liste
            records = payload
        else:
            logger.warning('Unexpected format for page: %s', type(payload))

        logger.info('Page start=%s returned %s records', start, len(records))

        if not records:
            # Plus d'enregistrements disponibles
            return

        # Retourner le lot d'enregistrements
        yield records

        # Vérifier si c'est la dernière page
        if len(records) < rows:
            return

        # Passer à la page suivante
        start += rows
