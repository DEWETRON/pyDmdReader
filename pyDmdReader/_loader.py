"""
Copyright DEWETRON GmbH 2021

Dmd reader library - DLL loader module
"""


import os
import sys
from ctypes import cdll
from . import _api
from .data_types import Version
from typing import List


_g_dmd_reader_api_dll = None


def _get_exposed_dmd_functions() -> List[str]:
    """Return a list of functions available in the dmd reader dll"""
    return [
        # Common
        #"DMDReader_GetVersion",
        #"DMDReader_Initialize",
        "DMDReader_Dispose",
        "DMDReader_OpenFile",
        "DMDReader_CloseFile",
        "DMDReader_GetNumChannels",
        "DMDReader_GetChannels",
        "DMDReader_GetVectorSampleType",
        "DMDReader_GetChannelInformation",
        # Channel data
        "DMDReader_GetSamplesWithTS_ScaledValue_Seconds",
        "DMDReader_GetSamplesAndTS_ScaledValue_Seconds",
        "DMDReader_GetSamplesWithTS_ReducedValue_Seconds",
        "DMDReader_GetSamplesAndTS_ReducedValue_Seconds",
        "DMDReader_GetSamplesWithTS_DigitalValue_Seconds",
        "DMDReader_GetSamplesAndTS_DigitalValue_Seconds",
        "DMDReader_GetSamplesAndTS_ScalarVector_Seconds",
        "DMDReader_GetSamplesAndTS_ComplexVector_Seconds",
        # Meta data
        "DMDReader_GetNumHeaderFields",
        "DMDReader_GetHeaderFields",
        "DMDReader_GetMeasurementStartTime",
        "DMDReader_GetNumMarkers",
        "DMDReader_GetMarkers",
        "DMDReader_GetNumDataSweeps",
        "DMDReader_GetDataSweeps",
        "DMDReader_GetNumReducedSweeps",
        "DMDReader_GetReducedSweeps",
        ("DMDReader_GetConfigurationXML", Version(1, 2)),
    ]

if sys.platform.startswith("win"):
    from win32api import GetFileVersionInfo, LOWORD, HIWORD
    def _get_version_number (filename) -> Version:
        # Under windows, we can query the DLL file directly
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return Version(HIWORD(ms), LOWORD(ms), HIWORD(ls))
else:
    def _get_version_number (filename) -> Version:
        # Under Linux, we need a different method
        return Version(0, 0)

class ApiLoader:
    """Dmd reader API loader class"""
    def __init__(self, filename):
        try:
            global _g_dmd_reader_api_dll

            # Load the dmd reader dll
            if sys.platform.startswith("win"):
                dll_file_paths = [os.path.join(os.path.dirname(__file__), "bin", filename)]
            else:
                dll_file_paths = [
                    filename,
                    os.path.join(os.path.dirname(__file__), "bin", filename),
                    ]

            # Try multiple file paths until one does not throw an exception
            for dll_file_path in dll_file_paths:
                try:
                    _g_dmd_reader_api_dll = cdll.LoadLibrary(dll_file_path)
                    break
                except FileNotFoundError:
                    pass

            for dmd_function in ("DMDReader_GetVersion", "DMDReader_Initialize"):
                setattr(_api, f"_{dmd_function}", getattr(_g_dmd_reader_api_dll, dmd_function))
            interface_version = _api.get_interface_version()
            _api.initialize(1, 0)

            version_info = _get_version_number(dll_file_path)
            setattr(_api, "_DMDReader_DllVersion", version_info)

            # Initialize all dmd reader functions
            for dmd_function in _get_exposed_dmd_functions():
                req_version = Version(1, 0)
                if len(dmd_function) == 2:
                    req_version = dmd_function[1]
                    if not interface_version.supports(req_version.major, req_version.minor):
                        continue
                    dmd_function = dmd_function[0]
                setattr(_api, f"_{dmd_function}", getattr(_g_dmd_reader_api_dll, dmd_function))

        except Exception as err:
            raise ImportError(f"DMD reader dll ({filename}) could not be loaded. ({err})")

    def __del__(self):
        try:
            global _g_dmd_reader_api_dll

            _api.dispose()

            # De-initialize all dmd reader functions
            for dmd_function in _get_exposed_dmd_functions():
                setattr(_api, dmd_function, None)

            _g_dmd_reader_api_dll = None
        except:
            pass
