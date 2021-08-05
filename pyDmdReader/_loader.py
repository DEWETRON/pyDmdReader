"""
Copyright DEWETRON GmbH 2021

Dmd reader library - DLL loader module
"""

from ctypes import cdll
import os
from . import _api
from typing import List

_g_dmd_reader_api_dll = None

def _get_exposed_dmd_functions() -> List[str]:
    """Return a list of fucntions available in the dmd reader dll"""
    return [
        # Common
        "DMDReader_GetVersion",
        "DMDReader_Initialize",
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
    ]

class ApiLoader:
    def __init__(self, filename):
        try:
            global _g_dmd_reader_api_dll

            # Load the dmd reader dll
            dll_file_path = os.path.normpath(os.path.abspath(filename))
            _g_dmd_reader_api_dll = cdll.LoadLibrary(dll_file_path)

            # Initialize all dmd reader functions
            for dmd_function in _get_exposed_dmd_functions():
                setattr(_api, "_{}".format(dmd_function), getattr(_g_dmd_reader_api_dll, dmd_function))

            _api.initialize(1, 0)

        except Exception as err:
            raise ImportError("DMD reader dll ({} could not be loaded)".format(filename))

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
