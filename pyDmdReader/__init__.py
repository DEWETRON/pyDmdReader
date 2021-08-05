"""
Python module to read Dewetron Oxygen DMD files

Example usage:
TODO
"""
__copyright__ = "Copyright 2021 DEWETRON GmbH"
__version__ = '0.0.1'

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
import os.path

DMDREADER_DLL_NAME = None
if '64' in platform.architecture()[0]:
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
    raise ImportError("OS ({} {}) not supported".format(sys.platform, platform.architecture()))

from . import _loader, _api
from ._dmd_reader import DmdReader
from .data_types import *

_module_loader = _loader.ApiLoader(os.path.join(os.path.dirname(__file__),  'bin', DMDREADER_DLL_NAME))

def dispose():
    """Close the dmd reader dll"""
    global _module_loader
    _module_loader = None
