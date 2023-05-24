"""
Copyright DEWETRON GmbH 2021

Dmd reader library - API module
"""

import inspect
from ctypes import byref, c_bool, c_char_p, c_double, c_int32, c_uint32, c_uint64, c_void_p
from typing import List, Optional, TYPE_CHECKING, Tuple

from ._structures import DmdChannelInformation, DmdDigitalSampleTimestamp, DmdHeaderField, DmdMarkerEvent, DmdReducedSampleTimestamp, \
    DmdSampleValueComplex, DmdSampleValueReduced, DmdScaledSampleTimeStamp, DmdSweep, DmdTimestampUtc
from .data_types import ChannelInformation, DateTimeZone, HeaderField, MarkerEvent, Sweep, Version
from .types import ErrorCode, SampleType

if TYPE_CHECKING:
    from .types import ChannelType
    from ctypes import Array

_DMDReader_GetVersion: Optional[type] = None
_DMDReader_Initialize: Optional[type] = None
_DMDReader_Dispose: Optional[type] = None
_DMDReader_OpenFile: Optional[type] = None
_DMDReader_CloseFile: Optional[type] = None
_DMDReader_GetChannels: Optional[type] = None
_DMDReader_GetNumChannels: Optional[type] = None
_DMDReader_GetVectorSampleType: Optional[type] = None
_DMDReader_GetChannelInformation: Optional[type] = None

_DMDReader_GetSamplesWithTS_ScaledValue_Seconds: Optional[type] = None
_DMDReader_GetSamplesAndTS_ScaledValue_Seconds: Optional[type] = None
_DMDReader_GetSamplesWithTS_ReducedValue_Seconds: Optional[type] = None
_DMDReader_GetSamplesAndTS_ReducedValue_Seconds: Optional[type] = None
_DMDReader_GetSamplesWithTS_DigitalValue_Seconds: Optional[type] = None
_DMDReader_GetSamplesAndTS_DigitalValue_Seconds: Optional[type] = None
_DMDReader_GetSamplesAndTS_ComplexVector_Seconds: Optional[type] = None
_DMDReader_GetSamplesAndTS_ScalarVector_Seconds: Optional[type] = None

_DMDReader_GetNumHeaderFields: Optional[type] = None
_DMDReader_GetHeaderFields: Optional[type] = None
_DMDReader_GetMeasurementStartTime: Optional[type] = None
_DMDReader_GetNumMarkers: Optional[type] = None
_DMDReader_GetMarkers: Optional[type] = None
_DMDReader_GetNumDataSweeps: Optional[type] = None
_DMDReader_GetDataSweeps: Optional[type] = None
_DMDReader_GetNumReducedSweeps: Optional[type] = None
_DMDReader_GetReducedSweeps: Optional[type] = None
_DMDReader_GetConfigurationXML: Optional[type] = None


def _check_loaded(func):
    """Decorator to check if the dll is already loaded"""

    def func_wrapper(*args, **kwargs):
        """Function wrapper"""
        try:
            return func(*args, **kwargs)
        except TypeError:
            raise Exception("DMD reader library not loaded")
        except Exception:
            raise

    return func_wrapper


def _check_error(error_code: int) -> None:
    """Helper function, to check given error_code"""
    error_code = ErrorCode(error_code)
    if error_code.value != 0:
        location = inspect.stack()[1][3]
        raise RuntimeError(f"Error in {location}() -> {error_code}")


# EXPORTED API FUNCTIONS


@_check_loaded
def get_version() -> Version:
    """DMD Reader API get version"""
    interface_version_major = c_uint32(0)
    interface_version_minor = c_uint32(0)
    error_code = _DMDReader_GetVersion(byref(interface_version_major), byref(interface_version_minor))
    _check_error(error_code)
    return Version(interface_version_major.value, interface_version_minor.value)


@_check_loaded
def initialize(interface_version_major: int, interface_version_minor: int) -> None:
    """DMD Reader API Initialization"""
    error_code = _DMDReader_Initialize(c_uint32(interface_version_major), c_uint32(interface_version_minor))
    _check_error(error_code)


@_check_loaded
def dispose() -> None:
    """DMD Reader unload API"""
    error_code = _DMDReader_Dispose()
    _check_error(error_code)


@_check_loaded
def open_file(filename: str) -> c_void_p:
    """DMD Reader API Open file"""
    file_handle = c_void_p()
    error_code = _DMDReader_OpenFile(c_char_p(filename.encode("utf-8")), byref(file_handle))
    _check_error(error_code)
    return file_handle


@_check_loaded
def close_file(file_handle: c_void_p) -> None:
    """DMD Reader API Close file"""
    error_code = _DMDReader_CloseFile(byref(file_handle))
    _check_error(error_code)


@_check_loaded
def get_num_channels(file_handle: c_void_p, channel_type: "ChannelType") -> int:
    """DMD Reader API Get number of channels"""
    num_channels = c_uint64(0)
    error_code = _DMDReader_GetNumChannels(file_handle, c_int32(channel_type.value), byref(num_channels))
    _check_error(error_code)
    return num_channels.value


@_check_loaded
def get_channels(
        file_handle: c_void_p, channel_type: "ChannelType", first_channel: int, max_channels: int
) -> Tuple[c_void_p, int]:
    """DMD Reader API Get channels"""
    channel_handle = c_void_p()
    num_channels = c_uint64(0)
    error_code = _DMDReader_GetChannels(
        file_handle,
        c_int32(channel_type.value),
        c_uint64(first_channel),
        c_uint64(max_channels),
        byref(channel_handle),
        byref(num_channels))
    _check_error(error_code)
    return channel_handle, num_channels.value


@_check_loaded
def get_vector_sample_types(channel_handle: c_void_p) -> Tuple[SampleType, SampleType, int]:
    """DMD Reader API Get vector sample types"""
    data_sample_type = c_int32(0)
    reduced_sample_type = c_int32(0)
    max_sample_dimension = c_uint32(0)
    error_code = _DMDReader_GetVectorSampleType(
        channel_handle, byref(data_sample_type), byref(reduced_sample_type), byref(max_sample_dimension)
    )
    _check_error(error_code)
    return SampleType(data_sample_type.value), SampleType(reduced_sample_type.value), max_sample_dimension.value


@_check_loaded
def get_channel_information(channel_handle: c_void_p) -> ChannelInformation:
    """DMD Reader API Get channel information"""
    channel_information = DmdChannelInformation()
    error_code = _DMDReader_GetChannelInformation(channel_handle, byref(channel_information))
    _check_error(error_code)
    return ChannelInformation(channel_information)


# READ SAMPLE VALUES INTO AN ARRAY

@_check_loaded
def get_samples_with_ts_scaled_value_seconds(
        channel_handle: c_void_p, first_sample: int, max_samples: int
) -> Tuple[int, int, "Array"]:
    """DMD Reader API Get samples with timestamps"""
    scaled_timestamp_values = (DmdScaledSampleTimeStamp * max_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesWithTS_ScaledValue_Seconds(
        channel_handle,
        c_uint64(first_sample),
        c_uint64(max_samples),
        byref(scaled_timestamp_values),
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, scaled_timestamp_values


@_check_loaded
def get_samples_and_ts_scaled_value_seconds(
        channel_handle: c_void_p, first_sample: int, max_samples: int
) -> Tuple[int, int, "Array", "Array"]:
    """
    DMD Reader API Get samples and timestamps
    Two separate arrays
    """
    samples = (c_double * max_samples)()
    timestamps = (c_double * max_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesAndTS_ScaledValue_Seconds(
        channel_handle,
        c_uint64(first_sample),
        c_uint64(max_samples),
        byref(samples),
        byref(timestamps),
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, samples, timestamps


@_check_loaded
def get_samples_with_ts_reduced_value_seconds(
        channel_handle: c_void_p, first_reduced_sample: int, max_reduced_samples: int
) -> Tuple[int, int, "Array"]:
    """DMD Reader API Get reduced samples with timestamps"""
    reduced_timestamp_values = (DmdReducedSampleTimestamp * max_reduced_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesWithTS_ReducedValue_Seconds(
        channel_handle,
        c_uint64(first_reduced_sample),
        c_uint64(max_reduced_samples),
        byref(reduced_timestamp_values),
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, reduced_timestamp_values


@_check_loaded
def get_samples_and_ts_reduced_value_seconds(
        channel_handle: c_void_p, first_reduced_sample: int, max_reduced_samples: int
) -> Tuple[int, int, "Array", "Array"]:
    """
    DMD Reader API Get samples only (uses _DMDReader_GetSamplesAndTS_ReducedValue_Seconds)
    Two separate arrays
    """
    reduced_samples = (DmdSampleValueReduced * max_reduced_samples)()
    reduced_timestamps = (c_double * max_reduced_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesAndTS_ReducedValue_Seconds(
        channel_handle,
        c_uint64(first_reduced_sample),
        c_uint64(max_reduced_samples),
        byref(reduced_samples),
        byref(reduced_timestamps),
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, reduced_samples, reduced_timestamps


@_check_loaded
def get_samples_with_ts_digital_value_seconds(
        channel_handle: c_void_p, first_sample: int, max_samples: int
) -> Tuple[int, int, "Array"]:
    """DMD Reader API Get samples with timestamps"""
    digital_timestamp_values = (DmdDigitalSampleTimestamp * max_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesWithTS_DigitalValue_Seconds(
        channel_handle,
        c_uint64(first_sample),
        c_uint64(max_samples),
        byref(digital_timestamp_values),
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, digital_timestamp_values


@_check_loaded
def get_samples_and_ts_digital_value_seconds(
        channel_handle: c_void_p, first_sample: int, max_samples: int
) -> Tuple[int, int, "Array", "Array"]:
    """
    DMD Reader API Get samples and timestamps
    Two separate arrays
    """
    samples = (c_int32 * max_samples)()
    timestamps = (c_double * max_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesAndTS_DigitalValue_Seconds(
        channel_handle,
        c_uint64(first_sample),
        c_uint64(max_samples),
        byref(samples),
        byref(timestamps),
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, samples, timestamps


@_check_loaded
def get_samples_and_ts_scalar_vector_seconds(
        channel_handle: c_void_p, first_sample: int, max_samples: int, max_sample_dimension: int
) -> Tuple[int, int, "Array", "Array"]:
    """DMD Reader API Get samples and timestamps"""
    samples = (c_double * (max_samples * max_sample_dimension))()
    timestamps = (c_double * max_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesAndTS_ScalarVector_Seconds(
        channel_handle,
        c_uint64(first_sample),
        c_uint64(max_samples),
        c_uint32(max_sample_dimension),
        byref(samples),
        byref(timestamps),
        None,
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, samples, timestamps


@_check_loaded
def get_samples_and_ts_complex_vector_seconds(
        channel_handle: c_void_p, first_sample: int, max_samples: int, max_sample_dimension: int
) -> Tuple[int, int, "Array", "Array"]:
    """DMD Reader API Get samples and timestamps"""
    samples = (DmdSampleValueComplex * (max_samples * max_sample_dimension))()
    timestamps = (c_double * max_samples)()
    num_valid_samples = c_uint64(0)
    next_sample = c_uint64(0)
    error_code = _DMDReader_GetSamplesAndTS_ComplexVector_Seconds(
        channel_handle,
        c_uint64(first_sample),
        c_uint64(max_samples),
        c_uint32(max_sample_dimension),
        byref(samples),
        byref(timestamps),
        None,
        byref(num_valid_samples),
        byref(next_sample)
    )
    _check_error(error_code)
    return num_valid_samples.value, next_sample.value, samples, timestamps


# READ FILE META DATA

@_check_loaded
def get_num_header_fields(file_handle: c_void_p) -> int:
    """DMD Reader API Get number of header fields"""
    num_header_fields = c_uint64(0)
    error_code = _DMDReader_GetNumHeaderFields(file_handle, byref(num_header_fields))
    _check_error(error_code)
    return num_header_fields.value


@_check_loaded
def get_header_fields(file_handle: c_void_p, first_field: int, max_fields: int) -> List[HeaderField]:
    """DMD Reader API Get number of header fields"""
    if max_fields <= 0:
        return []
    header_fields = (DmdHeaderField * max_fields)()
    num_header_fields = c_uint64(0)
    error_code = _DMDReader_GetHeaderFields(
        file_handle,
        c_uint64(first_field),
        c_uint64(max_fields),
        byref(header_fields),
        byref(num_header_fields)
    )
    _check_error(error_code)
    return [HeaderField(header_fields[i]) for i in range(0, num_header_fields.value)]


@_check_loaded
def get_measurement_start_time(file_handle: c_void_p, utc: bool) -> DateTimeZone:
    """DMD Reader API Get measurement start time"""
    timestamp = DmdTimestampUtc()
    error_code = _DMDReader_GetMeasurementStartTime(file_handle, byref(timestamp), c_bool(utc))
    _check_error(error_code)
    return DateTimeZone(timestamp)


@_check_loaded
def get_num_markers(file_handle: c_void_p) -> int:
    """DMD Reader API Get number of markers"""
    num_markers = c_uint64(0)
    error_code = _DMDReader_GetNumMarkers(file_handle, byref(num_markers))
    _check_error(error_code)
    return num_markers.value


@_check_loaded
def get_markers(file_handle: c_void_p, first_marker: int, max_markers: int) -> List[MarkerEvent]:
    """DMD Reader API Get event markers"""
    if max_markers <= 0:
        return []
    markers = (DmdMarkerEvent * max_markers)()
    num_markers = c_uint64(0)
    error_code = _DMDReader_GetMarkers(
        file_handle, c_uint64(first_marker), c_uint64(max_markers), byref(markers), byref(num_markers)
    )
    _check_error(error_code)
    return [MarkerEvent(markers[i]) for i in range(0, num_markers.value)]


@_check_loaded
def get_num_data_sweeps(channel_handle: c_void_p) -> int:
    """DMD Reader API Get number of data sweeps"""
    num_sweeps = c_uint64(0)
    error_code = _DMDReader_GetNumDataSweeps(channel_handle, byref(num_sweeps))
    _check_error(error_code)
    return num_sweeps.value


@_check_loaded
def get_data_sweeps(channel_handle: c_void_p, first_sweep: int, max_sweeps: int) -> List[Sweep]:
    """DMD Reader API Get data sweeps"""
    if max_sweeps <= 0:
        return []
    sweeps = (DmdSweep * max_sweeps)()
    num_sweeps = c_uint64(0)
    error_code = _DMDReader_GetDataSweeps(
        channel_handle, c_uint64(first_sweep), c_uint64(max_sweeps), byref(sweeps), byref(num_sweeps)
    )
    _check_error(error_code)
    return [Sweep(sweeps[i]) for i in range(0, num_sweeps.value)]


@_check_loaded
def get_num_reduced_sweeps(channel_handle: c_void_p) -> int:
    """DMD Reader API Get number of reduced data sweeps"""
    num_reduced_sweeps = c_uint64(0)
    error_code = _DMDReader_GetNumReducedSweeps(channel_handle, byref(num_reduced_sweeps))
    _check_error(error_code)
    return num_reduced_sweeps.value


@_check_loaded
def get_reduced_sweeps(channel_handle: c_void_p, first_reduced_sweep: int, max_reduced_sweeps: int) -> List[Sweep]:
    """DMD Reader API Get reduced data sweeps"""
    if max_reduced_sweeps <= 0:
        return []
    reduced_sweeps = (DmdSweep * max_reduced_sweeps)()
    num_reduced_sweeps = c_uint64(0)
    error_code = _DMDReader_GetReducedSweeps(
        channel_handle,
        c_uint64(first_reduced_sweep),
        c_uint64(max_reduced_sweeps),
        byref(reduced_sweeps),
        byref(num_reduced_sweeps)
    )
    _check_error(error_code)
    return [Sweep(reduced_sweeps[i]) for i in range(0, num_reduced_sweeps.value)]


@_check_loaded
def get_configuration_xml(file_handle: c_void_p) -> Optional[bytes]:
    """DMD Reader API Get the file configuration"""
    config = c_char_p()
    error_code = _DMDReader_GetConfigurationXML(file_handle, byref(config))
    _check_error(error_code)
    return config.value
