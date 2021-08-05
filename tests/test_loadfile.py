import pytest
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
