# DEWETRON pyDmdReader

pyDmdReader is a Python wrapper for the [Dewetron](https://www.dewetron.com/) DMD Reader API.
It allows to conveniently read DMD files that were recorded with the [Dewetron Oxygen](https://www.dewetron.com/products/oxygen-measurement-software/) measurement software.

# Installation

Currently, the package needs to be installed by using github release archives.
Direct integration into the Python Package Index is planned in the future.

## Microsoft Windows

The pyDmdReader python package can be installed with

```
python3 -m pip install https://github.com/DEWETRON/pyDmdReader/archive/refs/tags/v0.4.0.tar.gz
```

Windows binaries (DMD reader DLLs) are installed automatically.

## Linux

Currently, we support pyDmdReader for Linux on Debian 10 Buster and Ubuntu 20.04 Focal.
Each Linux distribution requires a separate rpm package to ensure no broken dependencies.
Contact Dewetron if you need support for another distribution or version.

The dmdreader packages can be found on the [current release](https://github.com/DEWETRON/pyDmdReader/releases/latest) page.
They need to be installed manually using the following command (adapt the filename to the one downloaded from the current release):

```
sudo apt install ./dewetron-dmd-reader-api_6.0.0-buster_amd64.deb
```

Now install pyDmdReader:
```
python3 -m pip install https://github.com/DEWETRON/pyDmdReader/archive/refs/tags/v0.4.0.tar.gz
```

If pip fails, please try manual installation:

You have to fullfill other python library dependencies:

```
pip3 install pandas
```

or run
```
pip3 install -r requirements.txt
```

This will automatically install numpy, which is also needed.

Do NOT install these packages using "apt".
These are outdated and incompatible with pyDmdReader.

# Example usage
There are example scripts in the examples subdirectory that show how to read DMD files in Python. A simple example looks like this:
```python
import pyDmdReader

dmd = pyDmdReader.DmdReader('my_recording.dmd')
print("Channels found in file: {}".format(dmd.channel_names))

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
    print("Channels: {}".format(dmd.channel_names))
```

## Testing

If you want to try out the DMD Reader and have no DMD files at hand, feel free to use example files from the [tests/data](https://github.com/DEWETRON/pyDmdReader/tree/main/tests/data) directory.

This repository comes with pytest compatible unit tests which can be started by calling `pytest` (or `python -m pytest`) from the root directoty of the repository.


# Contact
For technical or other DMD reader related questions please contact:

- Michael Oberhofer <michael.oberhofer@dewetron.com>
- Gunther Laure <gunther.laure@dewetron.com>
- Matthias Straka <matthias.straka@dewetron.com>

# License
MIT License

Copyright (c) 2021-2022 DEWETRON

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
