# DEWETRON pyDmdReader

pyDmdReader is a Python wrapper for the Dewetron DMD Reader API 


# Installation

## Windows

It should be sufficient to call

```
python3 -m pip install https://github.com/DEWETRON/pyDmdReader/archive/refs/tags/5.6.0.tar.gz
```


## Debian Buster 

Download and install the dmdreader debian package.

Installation is done using:

```
sudo apt install ./dewetron-dmd-reader-api_5.6.0-buster_amd64.deb
```

Now install pydmdreader:
```
python3 -m pip install https://github.com/DEWETRON/pyDmdReader/archive/refs/tags/5.6.0.tar.gz
```


If pip fails, please try manual installation:


You have to fullfill other py library dependencies:

```
pip3 install pandas
```

This will automatically numpy which is also needed.

Do NOT install these packages using "apt".
These are outdated and incompatible to pydmdreader.


**For technical questions please contact:**

Michael Oberhofer 

michael.oberhofer@dewetron.com

Gunther Laure

gunther.laure@dewetron.com




# License
MIT License

Copyright (c) 2021 DEWETRON

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
