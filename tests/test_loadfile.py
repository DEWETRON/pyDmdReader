"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""


import os
import pytest
from pyDmdReader.types import MarkerEventSource, MarkerEventType
from pyDmdReader import DmdReader


SIMPLE_DMD = os.path.join(os.path.dirname(__file__), "data", "simple.dmd")
DUPNAMES_DMD = os.path.join(os.path.dirname(__file__), "data", "duplicate_names.dmd")
INTERNAL_DMD = "DMD_DEMO_FILE"


def test_check_version():
    with DmdReader(SIMPLE_DMD) as dmd:
        version = dmd.version
        assert version.major == 1
        assert version.minor == 1


def test_check_channelnames():
    with DmdReader(SIMPLE_DMD) as dmd:
        names = dmd.channel_names
        assert len(names) == 10
        assert names[0] == "AI 1/I1 Sim"


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
    assert markers[1].time == pytest.approx(0.6331)

    assert dmd.measurement_duration == pytest.approx(0.6331)

    dmd.close()

def test_duplicate_names():
    with DmdReader(DUPNAMES_DMD) as dmd:
        assert len(dmd.channel_names) == 4
        assert dmd.channel_names[0] == dmd.channel_names[1]
        assert dmd.channel_names[2] == dmd.channel_names[3]
        with pytest.raises(KeyError):
            dmd.channels[dmd.channel_names[0]]

        assert dmd.allchannels[dmd.channel_ids[0]].name == "AI 1/1 Sim"
        assert dmd.allchannels[dmd.channel_ids[1]].name == "AI 1/1 Sim"
