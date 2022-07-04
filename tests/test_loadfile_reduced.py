"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""


import os
import pandas as pd
import pytest
from pyDmdReader import DmdReader, TimestampFormat


SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data", "simple.dmd")
SYNCASYNC_DMD = os.path.join(os.path.dirname(__file__), "data", "syncasync.dmd")
INTERNAL_DMD = "DMD_DEMO_FILE"


def test_check_invalid_name():
    dmd = DmdReader(INTERNAL_DMD)
    with pytest.raises(KeyError):
        dmd.read_reduced("INVALID")
    dmd.close()


def test_check_timestamp_none():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_reduced(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
    # No reduced sweeps in simple DMD
    assert data.empty
    column_names = list(data.columns)
    assert len(column_names) == 4
    assert column_names == ["MIN", "MAX", "AVG", "RMS"]
    assert isinstance(data.index, pd.Index)
    dmd.close()

def test_check_syncasync():
    with DmdReader(SYNCASYNC_DMD) as dmd:
        data = dmd.read_reduced(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
        # No reduced sweeps in simple DMD
        assert data.shape == (2,4)
        assert list(data.columns) == ["MIN", "MAX", "AVG", "RMS"]
        assert isinstance(data.index, pd.Index)

        data = dmd.read_reduced(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE, max_samples=1)
        assert data.shape == (1,4)
