"""
Copyright DEWETRON GmbH 2021

Dmd reader library - DLL structure module
"""


from ctypes import Structure, c_double, c_bool, c_int32, c_uint64, c_char_p
from typing import Union


class DmdSampleValueComplex(Structure):
    """Defines the data type for single complex value."""
    _fields_ = [
        ("real", c_double),
        ("imag", c_double),
    ]


class DmdSampleValueReduced(Structure):
    """Defines the data type for single reduced sample value."""
    _fields_ = [
        ("min", c_double),
        ("max", c_double),
        ("avg", c_double),
        ("rms", c_double),
    ]


class DmdTimestampUtc(Structure):
    """Specifies the Timestamp Format."""
    _fields_ = [
        ("year", c_int32),
        ("day_of_year", c_int32),
        ("time_of_day", c_double),
        ("time_offset", c_int32),
        ("valid", c_bool),
    ]


class DmdScaledSampleTimeStamp(Structure):
    """Specifies the tuple scaled sample value and timestamp in seconds."""
    _fields_ = [
        ("value", c_double),
        ("timestamp", c_double),
    ]


class DmdReducedSampleTimestamp(Structure):
    """Specifies the tuple reduced sample value and timestamp in seconds."""
    _fields_ = [
        ("value", DmdSampleValueReduced),
        ("timestamp", c_double),
    ]


class DmdDigitalSampleTimestamp(Structure):
    """Specifies the tuple reduced sample value and timestamp in seconds."""
    _fields_ = [
        ("value", c_int32),
        ("timestamp", c_double),
    ]


class DmdHeaderField(Structure):
    """Specifies a single header field in the dmd file."""
    _fields_ = [
        ("name", c_char_p),
        ("value", c_char_p),
    ]


class DmdChannelInformation(Structure):
    """Specifies the channel information."""
    _fields_ = [
        ("sample_rate", c_double),
        ("type", c_int32),
        ("name", c_char_p),
        ("unit", c_char_p),
        ("description", c_char_p),
        ("measurement_duration", c_double),
        ("range_min", c_double),
        ("range_max", c_double),
    ]


class DmdMarkerEvent(Structure):
    """Specifies the marker event data."""
    _fields_ = [
        ("source", c_int32),
        ("type", c_int32),
        ("time", c_double),
        ("text", c_char_p),
    ]


class DmdSweep(Structure):
    """Specifies a single sweep of data."""
    _fields_ = [
        ("first_sample", c_uint64),
        ("last_sample", c_uint64),
        ("start_time", c_double),
        ("end_time", c_double),
        ("sample_frequency", c_double),
    ]


DmdStructures = Union[
    DmdSampleValueComplex,
    DmdSampleValueReduced,
    DmdTimestampUtc,
    DmdScaledSampleTimeStamp,
    DmdReducedSampleTimestamp,
    DmdDigitalSampleTimestamp,
    DmdHeaderField,
    DmdChannelInformation,
    DmdMarkerEvent,
    DmdSweep,
]
