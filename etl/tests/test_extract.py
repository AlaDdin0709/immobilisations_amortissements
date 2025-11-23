import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
import json
from unittest.mock import MagicMock, patch
from extract import fetch_via_export_json, fetch_all_records_paginated


class DummyResp:
    def __init__(self, payload):
        self._payload = payload
    def raise_for_status(self):
        return None
    def json(self):
        return self._payload


def test_fetch_via_export_json_list():
    payload = [
        {"ndeg_immobilisation": "1001", "publication": "2022"},
        {"ndeg_immobilisation": "1002", "publication": "2022"}
    ]
    with patch('extract.requests.get', return_value=DummyResp(payload)) as mocked_get:
        records = fetch_via_export_json()
        assert isinstance(records, list)
        assert len(records) == 2
        assert records[0]["ndeg_immobilisation"] == "1001"


def test_fetch_all_records_paginated():
    # simulate two pages then empty
    page1 = {"results": [{"fields": {"ndeg_immobilisation": "2001"}}]}
    page2 = {"results": []}
    calls = [DummyResp(page1), DummyResp(page2)]

    def side_effect(url, params=None, timeout=None):
        return calls.pop(0)

    with patch('extract.requests.get', side_effect=side_effect):
        records = fetch_all_records_paginated(max_records=200)
        assert isinstance(records, list)
        assert len(records) == 1
        # record shape may be dict with 'fields'
        assert records[0].get('fields') is not None
