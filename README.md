# DEWETRON pyDmdReader

pyDmdReader is a Python wrapper for the [Dewetron](https://www.dewetron.com/) DMD Reader API.
It allows to conveniently read DMD files that were recorded with the [Dewetron Oxygen](https://www.dewetron.com/products/oxygen-measurement-software/) measurement software.

# Installation

Currently, the package needs to be installed by using github release archives.
Direct integration into the Python Package Index is planned in the future.

## Microsoft Windows

The latest release pyDmdReader Python package can be installed with

```cmd
pip install https://github.com/DEWETRON/pyDmdReader/archive/refs/tags/v7.2.1.tar.gz
```

Alternatively, you can install the current development version using
```cmd
pip install git+https://github.com/DEWETRON/pyDmdReader.git
```

Windows binaries (DMD reader DLLs) are installed automatically.

## Linux

Currently, we support pyDmdReader for Linux on Debian, Ubuntu and RHEL.
Each Linux distribution requires a separate rpm package to ensure no broken dependencies.
Contact Dewetron if you need support for another distribution or version.

The dmdreader packages can be found on the [current release](https://github.com/DEWETRON/pyDmdReader/releases/latest) page.
They need to be installed manually using the following command (adapt the filename to the one downloaded from the current release):

Example for Ubuntu 22.04 12 "jammy":
```bash
sudo apt install ./dewetron-dmd-reader-api_7.1.0.216~release-jammy_amd64.deb
```

Now install pyDmdReader (as user):
```bash
python3 -m pip install https://github.com/DEWETRON/pyDmdReader/archive/refs/tags/v7.2.1.tar.gz --user
```
or install the current development version using
```bash
python3 -m pip install git+https://github.com/DEWETRON/pyDmdReader.git --user
```

If pip fails, please try manual installation:

You have to fullfill other python library dependencies:

```
pip3 install pandas --user
```

or run
```
pip3 install -r requirements.txt
```

This will automatically install numpy, which is also needed.

Do NOT install these packages using `apt`.
These are outdated and incompatible with pyDmdReader.

# Example usage
There are example scripts in the examples subdirectory that show how to read DMD files in Python. A simple example looks like this:
```python
import pyDmdReader

dmd = pyDmdReader.DmdReader('my_recording.dmd')
print(f"Channels found in file: {dmd.channel_names}")

# Read configuration of first channel
first_channel = dmd.channels[dmd.channel_names[0]]
print(f"Name: {first_channel.name}")
print(f"Unit: {first_channel.unit}")
print(f"Samplerate: {first_channel.sample_rate} Hz")

# Read all data from channel 'AI 1/1'
data = dmd.read_dataframe('AI 1/1')
print(data)

# Read data from channel 'AI 1/1' from 1s to 3s after recording start
data = dmd.read_dataframe('AI 1/1', start_time = 1, end_time = 3)

dmd.close()
```

It is also possible to scope the DMD reader lifetime to avoid forgetting to call `close()`
```python
import pyDmdReader
with pyDmdReader.DmdReader('name.dmd') as dmd:
    print(f"Channels: {dmd.channel_names}")
```

## Dealing with duplicate channel names
When the DMD file has duplicate channel names, it is not possible to read data by using the channel name as a key (this will throw an exception if duplicate names are found).
Instead, it is possible to access channels by a unique ID.
```python
import pyDmdReader

with pyDmdReader.DmdReader('my_recording.dmd') as dmd:
    print(f"Channels found in file: {dmd.channel_names}")

    # Read first two channels
    data = dmd.read_dataframe(dmd.channel_ids[0:2])
    print(data)
```

In order to retrieve the channel name or other information of a channel with a unique ID, use the `allchannels` property of the `DmdReader`, which maps a channel id to the channel information.
When there are no duplicate channel names, it is possible to use the `channels` property, which uses channel names as the map key.

## Testing

If you want to try out the DMD Reader and have no DMD files at hand, feel free to use example files from the [tests/data](https://github.com/DEWETRON/pyDmdReader/tree/main/tests/data) directory.

This repository comes with pytest compatible unit tests which can be started by calling `pytest` (or `python -m pytest`) from the root directoty of the repository.


# Contact
For technical or other DMD reader related questions please contact:

- Gunther Laure <gunther.laure@dewetron.com>
- Matthias Straka <matthias.straka@dewetron.com>

# License
MIT License

Copyright (c) 2021-2024 DEWETRON

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
LICENSE (END)
