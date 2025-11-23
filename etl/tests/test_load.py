import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
import pandas as pd
from load import upsert_immobilisations


class DummyConn:
    def __init__(self):
        self.execs = []
    def execute(self, stmt, params):
        self.execs.append(params)
    def commit(self):
        pass
    def close(self):
        pass


class DummyEngine:
    def __init__(self, conn):
        self._conn = conn
    def connect(self):
        return self._conn


def test_upsert_skips_missing_pk(monkeypatch):
    # prepare dataframe with one valid and one missing PK
    rows = [
        {'ndeg_immobilisation': 'K1', 'publication': '2020', 'properties': {}},
        {'ndeg_immobilisation': None, 'publication': '2020', 'properties': {}}
    ]
    df = pd.DataFrame(rows)

    conn = DummyConn()
    engine = DummyEngine(conn)

    # monkeypatch get_engine to return our dummy engine
    import load as load_mod
    monkeypatch.setattr(load_mod, 'get_engine', lambda: engine)

    inserted = upsert_immobilisations(df, table_name='immobilisations_amortissements')

    # only one row should be executed
    assert inserted == 1
    assert len(conn.execs) == 1
    assert conn.execs[0]['ndeg_immobilisation'] == 'K1'
