"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""
import pandas
from pyDmdReader import DmdReader, TimestampFormat
import os.path
import pytest

SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data/simple.dmd")
INTERNAL_DMD = 'DMD_DEMO_FILE'

def test_check_invalid_name():
    dmd = DmdReader(INTERNAL_DMD)
    with pytest.raises(KeyError):
        dmd.read_reduced("INVALID")
    dmd.close()

def test_check_timestamp_none():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_reduced(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
    assert len(data) == 0 # No reduced sweeps in simple DMD
    column_names = [c for c in data.columns]
    assert len(column_names) == 4
    assert column_names == ["MIN", "MAX", "AVG", "RMS"]
    #assert type(data.index) is pandas.RangeIndex
    dmd.close()
