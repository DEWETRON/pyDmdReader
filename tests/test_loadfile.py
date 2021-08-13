"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""
from pyDmdReader.types import MarkerEventSource, MarkerEventType
from pyDmdReader import DmdReader
import os.path

SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data/simple.dmd")
INTERNAL_DMD = 'DMD_DEMO_FILE'

def test_check_version():
    dmd = DmdReader(SIMPLE_DMD)
    version = dmd.version
    assert version.major == 1
    assert version.minor == 1
    dmd.close()

def test_check_channelnames():
    dmd = DmdReader(SIMPLE_DMD)
    names = dmd.channel_names
    assert len(names) == 10
    assert names[0] == 'AI 1/I1 Sim'
    dmd.close()

def test_headers():
    dmd = DmdReader(SIMPLE_DMD)
    headers = dmd.headers
    assert len(headers) == 0
    dmd.close()

def test_markers():
    dmd = DmdReader(SIMPLE_DMD)
    markers = dmd.markers
    assert len(markers) == 2

    assert markers[0].source == MarkerEventSource.SOURCE_MANUAL
    assert markers[0].type == MarkerEventType.START
    assert markers[0].text == "Recording Start"
    assert markers[0].time == 0

    assert markers[1].source == MarkerEventSource.SOURCE_MANUAL
    assert markers[1].type == MarkerEventType.STOP
    assert markers[1].text == "Recording Stop"
    assert markers[1].time >= 0.633

    assert round(dmd.measurement_duration, 4) == 0.6331

    dmd.close()
