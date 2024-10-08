"""
Copyright DEWETRON GmbH 2022

Dmd reader library - Unit Tests for internal demo DMD datatypes
"""


import pyDmdReader


DMD_FILE = "DMD_DEMO_FILE"


def test_check_demo_file():
    dmd = pyDmdReader.DmdReader(DMD_FILE)
    assert dmd.version.major == 1 and dmd.version.minor >= 1

    assert len(dmd.channel_names) >= 5

    assert dmd.channel_names[0] == "AI 0/0 (Demo)"
    channel = dmd.channels["AI 0/0 (Demo)"]
    assert channel.description == "DEMO Analog"
    assert channel.unit == "V"
    assert channel.sample_rate == 10000.0
    assert channel.dtype == "float64"
    data = dmd.read_dataframe("AI 0/0 (Demo)")
    assert len(data) == 40002
    assert len(data.columns) == 1
    assert data.dtypes[0] == "float64"

    assert dmd.channel_names[1] == "Cnt 0/0 (Demo)"
    channel = dmd.channels["Cnt 0/0 (Demo)"]
    assert channel.dtype == "float64"
    data = dmd.read_dataframe("Cnt 0/0 (Demo)")
    assert len(data) == 10000
    assert len(data.columns) == 1
    assert data.dtypes[0] == "float64"

    assert dmd.channel_names[2] == "DI 1/1 (Demo)"
    channel = dmd.channels["DI 1/1 (Demo)"]
    assert channel.dtype == "i4"
    data = dmd.read_dataframe("DI 1/1 (Demo)")
    assert len(data) == 10000
    assert len(data.columns) == 1
    assert data.dtypes[0] == "int32"
    assert data.iloc[0].name == 0.000
    assert data.iloc[0][0] == 0
    assert data.iloc[1].name == 0.001
    assert data.iloc[1][0] == 1

    assert dmd.channel_names[3] == "VC 1/1 (Demo)"
    channel = dmd.channels["VC 1/1 (Demo)"]
    assert channel.dtype == "complex128"
    data = dmd.read_dataframe("VC 1/1 (Demo)")
    assert len(data) == 10000
    assert len(data.columns) == 5
    assert data.dtypes[0] == "complex128"

    assert dmd.channel_names[4] == "VS 1/1 (Demo)"
    channel = dmd.channels["VS 1/1 (Demo)"]
    assert channel.dtype == "float64"
    data = dmd.read_dataframe("VS 1/1 (Demo)")
    assert len(data) == 10000
    assert len(data.columns) == 10
    assert data.columns[0] == "VS 1/1 (Demo)[0]"
    assert data.dtypes[0] == "float64"
    assert data.iloc[0].name == 0.000
    assert sum(abs(data.iloc[0] - [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])) < 1e-15

    dmd.close()

def test_check_demo_file_unique_ids():
    dmd = pyDmdReader.DmdReader(DMD_FILE)
    assert dmd.version.major == 1 and dmd.version.minor >= 1

    assert len(dmd.channel_names) == len(dmd.channel_ids)

    channel = dmd.channels["AI 0/0 (Demo)"]
    unique_id = channel.handle.value
    channel2 = dmd.allchannels[unique_id]
    assert channel.name == channel2.name
    assert channel == channel2

def test_check_demo_file_multicolumn():
    dmd = pyDmdReader.DmdReader(DMD_FILE)
    data = dmd.read_dataframe(["Cnt 0/0 (Demo)", "DI 1/1 (Demo)", "VS 1/1 (Demo)"])

    assert len(data.dtypes) == 12
    assert data.dtypes[0] == "float64"
    assert data.dtypes[1] == "int32"
    assert data.dtypes[2] == "float64"

    dmd.close()

def test_version():
    v = pyDmdReader.Version(1,2)
    assert v.major == 1
    assert v.minor == 2
    assert v.micro == 0
    assert str(v) == "1.2"

    v = pyDmdReader.Version(1,2,3)
    assert v.major == 1
    assert v.minor == 2
    assert v.micro == 3
    assert str(v) == "1.2.3"

    assert str(pyDmdReader.Version.parse("9.8")) == "9.8"
    assert str(pyDmdReader.Version.parse("9.8.7")) == "9.8.7"
