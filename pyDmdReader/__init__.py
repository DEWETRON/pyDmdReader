"""
Copyright DEWETRON GmbH 2022

Python module to read Dewetron Oxygen DMD files

Example usage:
dmd_file = pyDmdReader.DmdReader("filename.dmd")
data = dmd_file.read_dataframe("channel_name")
dmd_file.close()
"""


__copyright__ = "Copyright 2022 DEWETRON GmbH"
__version__ = "0.5.0"


__all__ = [
    "data_types",
    "types",
    "_api",
    "_channel_config",
    "_dmd_reader",
    "_loader",
    "_structures",
]


import platform
import sys


DMDREADER_DLL_NAME = None
if "64" in platform.architecture()[0]:
    if sys.platform.startswith("win"):
        DMDREADER_DLL_NAME = "dmd_reader_api_x64.dll"
    elif sys.platform.startswith("linux"):
        DMDREADER_DLL_NAME = "libdmd_reader_api_x64.so"
else:
    if sys.platform.startswith("win"):
        DMDREADER_DLL_NAME = "dmd_reader_api.dll"
    elif sys.platform.startswith("linux"):
        DMDREADER_DLL_NAME = "libdmd_reader_api.so"

if not DMDREADER_DLL_NAME:
    raise ImportError(f"OS ({sys.platform} {platform.architecture()}) not supported")


from . import _loader, _api
from ._dmd_reader import DmdReader, TimestampFormat
from .data_types import *


_module_loader = _loader.ApiLoader(DMDREADER_DLL_NAME)


def dispose():
    """Close the dmd reader dll"""
    global _module_loader
    _module_loader = None
