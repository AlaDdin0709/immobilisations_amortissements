import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
import pandas as pd
from load import upsert_immobilisations


class DummyConn:
    def __init__(self):
        self.execs = []

    def execute(self, *args, **kwargs):
        # record the call args for inspection
        self.execs.append({'args': args, 'kwargs': kwargs})

    def commit(self):
        pass

    def close(self):
        pass


class DummyEngine:
    def __init__(self, conn):
        self._conn = conn
    def connect(self):
        return self._conn


def test_upsert_inserts_rows_with_pk(monkeypatch):
    # loader expects ndeg_immobilisation to be present (transform guarantees it)
    rows = [
        {'ndeg_immobilisation': 'K1', 'publication': '2020', 'valeur_d_acquisition': 123.45}
    ]
    df = pd.DataFrame(rows)

    conn = DummyConn()
    engine = DummyEngine(conn)

    # monkeypatch get_engine to return our dummy engine
    import load as load_mod
    monkeypatch.setattr(load_mod, 'get_engine', lambda: engine)

    inserted = upsert_immobilisations(df, table_name='immobilisations_amortissements')

    # one upsert attempt should have been made
    assert inserted == 1
    assert len(conn.execs) == 1
