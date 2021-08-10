"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""
import numpy as np
from pyDmdReader import DmdReader, TimestampFormat
import os.path
import pytest

SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data/simple.dmd")
INTERNAL_DMD = 'DMD_DEMO_FILE'

def test_check_invalid_name():
    dmd = DmdReader(INTERNAL_DMD)
    with pytest.raises(KeyError):
        dmd.get_data_array("INVALID")

def test_check_timestamp_none():
    dmd = DmdReader(INTERNAL_DMD)
    data, timestamps = dmd.get_data_array(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
    assert timestamps is None
    assert len(data) == 40002
    assert data.dtype is np.dtype('float64')

def test_check_timestamp_seconds():
    dmd = DmdReader(INTERNAL_DMD)
    data, timestamps = dmd.get_data_array(dmd.channel_names[0], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 40002
    assert len(timestamps) == 40002
    assert data.dtype is np.dtype('float64')
    assert timestamps.dtype is np.dtype('float64')
    assert timestamps[0] == 1

def test_check_timestamp_absolute_local():
    dmd = DmdReader(SIMPLE_DMD)
    data, timestamps = dmd.get_data_array(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_LOCAL_TIME)
    assert len(data) == 6331
    assert data.dtype is np.dtype('float64')
    assert timestamps.dtype == np.dtype('datetime64[ns]')
    assert timestamps[0] == np.datetime64('2021-08-05T12:21:27.2708')

def test_check_timestamp_absolute_utc():
    dmd = DmdReader(SIMPLE_DMD)
    data, timestamps = dmd.get_data_array(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME)
    assert len(data) == 6331
    assert data.dtype is np.dtype('float64')
    assert timestamps.dtype == np.dtype('datetime64[ns]')
    assert timestamps[0] == np.datetime64('2021-08-05T10:21:27.2708')

def test_check_vector():
    dmd = DmdReader(INTERNAL_DMD)
    data, _ = dmd.get_data_array('VS 1/1 (Demo)', timestamp_format=TimestampFormat.NONE)
    assert data.shape == (10, 10000)
    assert data.dtype is np.dtype('float64')

def test_check_complex_vector():
    dmd = DmdReader(INTERNAL_DMD)
    data, _ = dmd.get_data_array('VC 1/1 (Demo)', timestamp_format=TimestampFormat.NONE)
    assert data.shape == (5, 10000)
    assert data.dtype is np.dtype('complex128')

def test_check_multicolumn():
    dmd = DmdReader(SIMPLE_DMD)
    data, timestamps = dmd.get_data_array(dmd.channel_names[0:2], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert data.shape == (2, 6331)
    assert len(timestamps) == 6331
    assert data.dtype is np.dtype('float64')
    assert timestamps.dtype is np.dtype('float64')
    assert timestamps[0] == 0
