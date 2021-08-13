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
        dmd.read_dataframe("INVALID")
    dmd.close()

def test_check_timestamp_none():
    dmd = DmdReader(INTERNAL_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
    assert len(data) == 40002
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.RangeIndex
    dmd.close()

def test_check_timestamp_seconds():
    dmd = DmdReader(INTERNAL_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 40002
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.Float64Index
    dmd.close()

def test_check_timestamp_absolute_local():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_LOCAL_TIME)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.DatetimeIndex
    assert data.iloc[0].name == pandas.Timestamp('2021-08-05T12:21:27.2708+0200', tz='UTC+02:00')
    dmd.close()

def test_check_timestamp_absolute_utc():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.DatetimeIndex
    assert data.iloc[0].name == pandas.Timestamp("2021-08-05T10:21:27.2708", tz="UTC")
    dmd.close()

def test_check_multichannel():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe([dmd.channel_names[0], dmd.channel_names[1]], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert column_names == [dmd.channel_names[0], dmd.channel_names[1]]
    dmd.close()

def test_check_multichannel_notimestamp():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.read_dataframe(dmd.channel_names[0:3], timestamp_format=TimestampFormat.NONE)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert column_names == dmd.channel_names[0:3]
    dmd.close()

def test_timerange_start():
    dmd = DmdReader(INTERNAL_DMD)
    # The file has two sweeps [1-2] and [5-8]
    data = dmd.read_dataframe(dmd.channel_names[0], start_time=3, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 30001
    assert type(data.index) is pandas.Float64Index
    assert data.index[0] == 5
    assert data.index[-1] == 8

    data = dmd.read_dataframe(dmd.channel_names[0], start_time=6, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 20001
    assert type(data.index) is pandas.Float64Index
    assert data.index[0] == 6
    assert data.index[-1] == 8

    data = dmd.read_dataframe(dmd.channel_names[0], start_time=0.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 40002
    assert type(data.index) is pandas.Float64Index
    assert data.index[0] == 1
    assert data.index[-1] == 8

    dmd.close()

def test_timerange_end():
    dmd = DmdReader(INTERNAL_DMD)
    # The file has two sweeps [1-2] and [5-8]
    data = dmd.read_dataframe(dmd.channel_names[0], end_time=3, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 10001
    assert type(data.index) is pandas.Float64Index
    assert data.index[0] == 1
    assert data.index[-1] == 2

    data = dmd.read_dataframe(dmd.channel_names[0], end_time=5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 10002
    assert type(data.index) is pandas.Float64Index
    assert data.index[0] == 1
    assert data.index[-1] == 5

    data = dmd.read_dataframe(dmd.channel_names[0], end_time=0.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 0

    data = dmd.read_dataframe(dmd.channel_names[0], end_time=1.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 5001
    assert type(data.index) is pandas.Float64Index
    assert data.index[0] == 1
    assert data.index[-1] == 1.5
    
    dmd.close()

def test_timerange_both():
    dmd = DmdReader(INTERNAL_DMD)
    # The file has two sweeps [1-2] and [5-8]
    data = dmd.read_dataframe(dmd.channel_names[0], start_time=1.5, end_time=5.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 10002
    assert type(data.index) is pandas.Float64Index
    assert data.index[0] == 1.5
    assert data.index[-1] == 5.5

    dmd.close()

def test_timerange_simple():
    dmd = DmdReader(SIMPLE_DMD)
    # The file has one sweeps [0 - 0.633] but a recording offset to acquisition start
    data = dmd.read_dataframe(dmd.channel_names[0], start_time=0, end_time=0.5, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 5001
    assert data.index[0] == 0
    assert data.index[-1] == 0.5

    data = dmd.read_dataframe(dmd.channel_names[0], start_time=0.1, end_time=0.4, timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 3001
    assert round(data.index[0], 2) == 0.1
    assert round(data.index[-1], 2) == 0.4

    dmd.close()
