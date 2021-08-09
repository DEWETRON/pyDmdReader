"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""
import pandas
from pyDmdReader import DmdReader, TimestampFormat
import os.path

SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data/simple.dmd")
INTERNAL_DMD = 'DMD_DEMO_FILE'

def test_check_version():
    dmd = DmdReader(SIMPLE_DMD)
    version = dmd.get_version()
    assert version.major == 1
    assert version.minor == 1

def test_check_channelnames():
    dmd = DmdReader(SIMPLE_DMD)
    names = dmd.channel_names
    assert len(names) == 10
    assert names[0] == 'AI 1/I1 Sim'

def test_check_timestamp_none():
    dmd = DmdReader(INTERNAL_DMD)
    data = dmd.get_data(dmd.channel_names[0], timestamp_format=TimestampFormat.NONE)
    assert len(data) == 40002
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.RangeIndex

def test_check_timestamp_seconds():
    dmd = DmdReader(INTERNAL_DMD)
    data = dmd.get_data(dmd.channel_names[0], timestamp_format=TimestampFormat.SECONDS_SINCE_START)
    assert len(data) == 40002
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.Float64Index

def test_check_timestamp_absolute_local():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.get_data(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_LOCAL_TIME)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.DatetimeIndex
    assert data.iloc[0].name == pandas.Timestamp('2021-08-05T12:21:27.2708+0200', tz='UTC+02:00')

def test_check_timestamp_absolute_utc():
    dmd = DmdReader(SIMPLE_DMD)
    data = dmd.get_data(dmd.channel_names[0], timestamp_format=TimestampFormat.ABSOLUTE_UTC_TIME)
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert len(column_names) == 1
    assert column_names[0] == dmd.channel_names[0]
    assert type(data.index) is pandas.DatetimeIndex
    assert data.iloc[0].name == pandas.Timestamp("2021-08-05T10:21:27.2708", tz="UTC")
