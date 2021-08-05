"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""
import pyDmdReader
import os.path

SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data/simple.dmd")

def test_check_version():
    dmd = pyDmdReader.DmdReader(SIMPLE_DMD)
    version = dmd.get_version()
    assert version.major == 1
    assert version.minor == 1

def test_check_channelnames():
    dmd = pyDmdReader.DmdReader(SIMPLE_DMD)
    names = dmd.channel_names
    assert len(names) == 10
    assert names[0] == 'AI 1/I1 Sim'

def test_check_channeldata():
    dmd = pyDmdReader.DmdReader(SIMPLE_DMD)
    data = dmd.get_data(dmd.channel_names[0])
    assert len(data) == 6331
    column_names = [c for c in data.columns]
    assert len(column_names) == 2
    assert column_names[0] == 'TIMESTAMPS'
    assert column_names[1] == 'DATA'
