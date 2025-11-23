import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from transform import _to_date, _to_int, _to_decimal, transform_records


def test_to_date_valid():
    assert _to_date('2021-02-05') is not None
    assert str(_to_date('2021-02-05')) == '2021-02-05'


def test_to_date_invalid():
    assert _to_date('invalid-date') is None
    assert _to_date('') is None


def test_to_int_and_decimal():
    assert _to_int('10') == 10
    assert _to_int(10.0) == 10
    assert _to_int(None) is None
    assert _to_decimal('3.14') == 3.14
    assert _to_decimal(None) is None


def test_transform_generates_surrogate_and_properties():
    # record without ndeg_immobilisation -> should generate surrogate
    recs = [
        {
            'publication': 'CA 2017',
            'collectivite': 'DEPARTEMENT',
            'nature': '2135',
            'date_d_acquisition': None,
            'ndeg_immobilisation': None,
            'valeur_d_acquisition': 1000.0
        }
    ]
    df, report = transform_records(recs)
    assert len(df) == 1
    # Should have generated a non-empty ndeg_immobilisation
    assert df.loc[0, 'ndeg_immobilisation'] is not None
    # properties should be a dict-like serialized to JSON later; here ensure column exists
    assert 'properties' in df.columns


def test_transform_handles_export_flat_records():
    # Simulate export JSON flat record (no 'fields')
    recs = [
        {
            'publication': '2022',
            'collectivite': 'VILLE',
            'ndeg_immobilisation': '1001',
            'valeur_d_acquisition': 2000.5
        }
    ]
    df, report = transform_records(recs)
    assert df.loc[0, 'ndeg_immobilisation'] == '1001'
    assert df.loc[0, 'valeur_d_acquisition'] == 2000.5
