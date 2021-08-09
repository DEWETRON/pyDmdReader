"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Unit Tests
"""
import pyDmdReader

DMD_FILE = 'DMD_DEMO_FILE'

def test_check_demo_file():
    dmd = pyDmdReader.DmdReader(DMD_FILE)
    version = dmd.get_version()
    assert version.major == 1 and version.minor == 1

    assert len(dmd.channel_names) >= 5

    assert dmd.channel_names[0] == 'AI 0/0 (Demo)'
    channel = dmd.channels['AI 0/0 (Demo)']
    assert channel.description == 'DEMO Analog'
    assert channel.unit == 'V'
    assert channel.sample_rate == 10000.0
    assert channel.dtype == 'float64'
    data = dmd.get_data('AI 0/0 (Demo)')
    assert len(data) == 40002
    assert len(data.columns) == 2
    assert data.dtypes[0] == 'float64'
    assert data.dtypes[1] == 'float64'

    assert dmd.channel_names[1] == 'Cnt 0/0 (Demo)'
    channel = dmd.channels['Cnt 0/0 (Demo)']
    assert channel.dtype == 'float64'
    data = dmd.get_data('Cnt 0/0 (Demo)')
    assert len(data) == 10000
    assert len(data.columns) == 2
    assert data.dtypes[0] == 'float64'
    assert data.dtypes[1] == 'float64'

    assert dmd.channel_names[2] == 'DI 1/1 (Demo)'
    channel = dmd.channels['DI 1/1 (Demo)']
    assert channel.dtype == 'i4'
    data = dmd.get_data('DI 1/1 (Demo)')
    assert len(data) == 10000
    assert len(data.columns) == 2
    assert data.dtypes[0] == 'float64'
    assert data.dtypes[1] == 'int32'

    assert dmd.channel_names[3] == 'VC 1/1 (Demo)'
    channel = dmd.channels['VC 1/1 (Demo)']
    assert channel.dtype == 'complex128'
    data = dmd.get_data('VC 1/1 (Demo)')
    assert len(data) == 10000
    assert len(data.columns) == 6
    assert data.dtypes[0] == 'float64'
    assert data.dtypes[1] == 'complex128'

    assert dmd.channel_names[4] == 'VS 1/1 (Demo)'
    channel = dmd.channels['VS 1/1 (Demo)']
    assert channel.dtype == 'float64'
    data = dmd.get_data('VS 1/1 (Demo)')
    assert len(data) == 10000
    assert len(data.columns) == 11
    assert data.dtypes[0] == 'float64'
    assert data.dtypes[1] == 'float64'
