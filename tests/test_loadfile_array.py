"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""


import os
import numpy as np
import pytest
from pyDmdReader import DmdReader, TimestampFormat


SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data", "simple.dmd")
DUPNAMES_DMD = os.path.join(os.path.dirname(__file__), "data", "duplicate_names.dmd")
INTERNAL_DMD = "DMD_DEMO_FILE"


def test_check_invalid_name():
    dmd = DmdReader(INTERNAL_DMD)
    with pytest.raises(KeyError):
        dmd.read_array("INVALID")
    dmd.close()


def test_check_timestamp_none():
    dmd = DmdReader(INTERNAL_DMD)
    data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
    assert timestamps is None
    assert len(data) == 40002
    assert data.dtype is np.dtype("float64")
    dmd.close()


def test_check_timestamp_seconds():
    dmd = DmdReader(INTERNAL_DMD)
    data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 40002
    assert len(timestamps) == 40002
    assert data.dtype is np.dtype("float64")
    assert timestamps.dtype is np.dtype("float64")
    assert timestamps[0] == 1
    dmd.close()


def test_check_timestamp_absolute_local():
    dmd = DmdReader(SIMPLE_DMD)
    data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_LOCAL_TIME)
    assert data.size == 6331
    assert data.dtype is np.dtype("float64")
    assert timestamps.dtype == np.dtype("datetime64[ns]")
    assert timestamps[0] == np.datetime64("2021-08-05T12:21:27.2708")
    dmd.close()


def test_check_timestamp_absolute_utc():
    dmd = DmdReader(SIMPLE_DMD)
    data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME)
    assert len(data) == 6331
    assert data.dtype is np.dtype("float64")
    assert timestamps.dtype == np.dtype("datetime64[ns]")
    assert timestamps[0] == np.datetime64("2021-08-05T10:21:27.2708")
    dmd.close()


def test_check_vector():
    dmd = DmdReader(INTERNAL_DMD)
    data, _ = dmd.read_array("VS 1/1 (Demo)", timestamp_format=TimestampFormat.NONE)
    assert data.shape == (10, 10000)
    assert data.dtype is np.dtype("float64")
    dmd.close()


def test_check_complex_vector():
    dmd = DmdReader(INTERNAL_DMD)
    data, _ = dmd.read_array("VC 1/1 (Demo)", timestamp_format=TimestampFormat.NONE)
    assert data.shape == (5, 10000)
    assert data.dtype is np.dtype("complex128")
    dmd.close()


def test_check_multicolumn():
    dmd = DmdReader(SIMPLE_DMD)
    data, timestamps = dmd.read_array(dmd.channel_names[0:2], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert data.shape == (2, 6331)
    assert len(timestamps) == 6331
    assert data.dtype is np.dtype("float64")
    assert timestamps.dtype is np.dtype("float64")
    assert timestamps[0] == 0
    dmd.close()

def test_duplicate_names():
    dmd = DmdReader(DUPNAMES_DMD)
    with pytest.raises(KeyError):
        dmd.read_array(dmd.channel_names[0])
    data, _ = dmd.read_array(dmd.channel_ids[0:4])

    assert len(data) == 4
    assert data.shape == (4, 208)

    assert data[0][0] != data[1][0]

    dmd.close()
