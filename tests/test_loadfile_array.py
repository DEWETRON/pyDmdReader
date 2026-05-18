"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""


import os
import numpy as np
import pytest
from pyDmdReader import DmdReader, TimestampFormat


DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
SIMPLE_DMD = os.path.join(DATA_PATH, "simple.dmd")
DUPNAMES_DMD = os.path.join(DATA_PATH, "duplicate_names.dmd")
INTERNAL_DMD = "DMD_DEMO_FILE"


def test_check_invalid_name():
    with DmdReader(INTERNAL_DMD) as dmd:
        with pytest.raises(KeyError):
            dmd.read_array("INVALID")


def test_check_timestamp_none():
    with DmdReader(INTERNAL_DMD) as dmd:
        data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
        assert timestamps is None
        assert len(data) == 40002
        assert data.dtype is np.dtype("float64")


def test_check_timestamp_seconds():
    with DmdReader(INTERNAL_DMD) as dmd:
        data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
        assert len(data) == 40002
        assert len(timestamps) == 40002
        assert data.dtype is np.dtype("float64")
        assert timestamps.dtype is np.dtype("float64")
        assert timestamps[0] == 1


def test_check_timestamp_absolute_local():
    with DmdReader(SIMPLE_DMD) as dmd:
        data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_LOCAL_TIME)
        assert data.size == 6331
        assert data.dtype is np.dtype("float64")
        assert timestamps.dtype == np.dtype("datetime64[ns]")
        assert timestamps[0] == np.datetime64("2021-08-05T12:21:27.2708")


def test_check_timestamp_absolute_utc():
    with DmdReader(SIMPLE_DMD) as dmd:
        data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME)
        assert len(data) == 6331
        assert data.dtype is np.dtype("float64")
        assert timestamps.dtype == np.dtype("datetime64[ns]")
        assert timestamps[0] == np.datetime64("2021-08-05T10:21:27.2708")


def test_check_max_samples():
    with DmdReader(INTERNAL_DMD) as dmd:
        data, timestamps = dmd.read_array(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE, max_samples=1234)
        assert timestamps is None
        assert len(data) == 1234
        assert data.dtype is np.dtype("float64")

def test_check_vector():
    with DmdReader(INTERNAL_DMD) as dmd:
        data, _ = dmd.read_array("VS 1/1 (Demo)", timestamp_format=TimestampFormat.NONE)
        assert data.shape == (10, 10000)
        assert data.dtype is np.dtype("float64")


def test_check_complex_vector():
    with DmdReader(INTERNAL_DMD) as dmd:
        data, _ = dmd.read_array("VC 1/1 (Demo)", timestamp_format=TimestampFormat.NONE)
        assert data.shape == (5, 10000)
        assert data.dtype is np.dtype("complex128")


def test_check_multicolumn():
    with DmdReader(SIMPLE_DMD) as dmd:
        data, timestamps = dmd.read_array(dmd.channel_names[0:2], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
        assert data.shape == (2, 6331)
        assert len(timestamps) == 6331
        assert data.dtype is np.dtype("float64")
        assert timestamps.dtype is np.dtype("float64")
        assert timestamps[0] == 0


def test_duplicate_names():
    with DmdReader(DUPNAMES_DMD) as dmd:
        with pytest.raises(KeyError):
            dmd.read_array(dmd.channel_names[0])
        data, _ = dmd.read_array(dmd.channel_ids[0:4])

        assert len(data) == 4
        assert data.shape == (4, 208)

        assert data[0][0] != data[1][0]
