"""
Copyright DEWETRON GmbH 2021

Dmd reader library - Module for all accessible data types returned by DmdReader functions
"""


from datetime import timezone, timedelta
from functools import total_ordering
from typing import TYPE_CHECKING
import pandas as pd
from .types import MarkerEventSource, MarkerEventType, ChannelType
if TYPE_CHECKING:
    from ._structures import DmdTimestampUtc, DmdHeaderField, DmdChannelInformation, DmdMarkerEvent, DmdSweep, \
        DmdStructures


class _ConverterBase:
    """Base class"""
    def __init__(self, structure: "DmdStructures"):
        for field in structure._fields_:
            field_name = field[0]
            field_value = getattr(structure, field_name)
            if isinstance(field_value, bytes):
                field_value = field_value.decode()
            setattr(self, field_name, field_value)

    def __repr__(self):
        return "{} ({})".format(self.__class__.__name__, ", ".join(
            [f"{key}: {value}" for key, value in self.__dict__.items()])
        )


class DateTimeZone(_ConverterBase):
    """Describes the Timestamp Format"""
    year = None
    day_of_year = None
    time_of_day = None
    time_offset = None
    valid = None

    def __init__(self, structure: "DmdTimestampUtc"):
        _ConverterBase.__init__(self, structure)

    @property
    def datetime(self) -> pd.Timestamp:
        """Get an according pandas Timestamp object"""
        tzinfo = timezone(timedelta(minutes=self.time_offset))

        return (
            pd.Timestamp(year=self.year, month=1, day=1, tz=tzinfo) +
            pd.Timedelta(self.day_of_year - 1, unit="days") +
            pd.Timedelta(self.time_of_day, unit="seconds")
        )

    def __str__(self):
        return str(self.datetime)


class HeaderField(_ConverterBase):
    """Describes a single header field"""
    name = None
    value = None

    def __init__(self, structure: "DmdHeaderField"):
        _ConverterBase.__init__(self, structure)


class ChannelInformation(_ConverterBase):
    """Describes the channel information"""
    # SampleRate [Hz]
    sample_rate = None
    # Channel Type
    type = None
    # Name of the channel
    name = None
    # Physical unit of the channel sample data
    unit = None
    # Description of the channel
    description = None
    # Measurement duration of the channel's sample data [seconds]
    measurement_duration = None
    # Minimum range of the channel's sample data. Specified in the physical unit of the channel
    range_min = None
    # Maximum range of the channel's sample data. Specified in the physical unit of the channel
    range_max = None

    def __init__(self, structure: "DmdChannelInformation"):
        _ConverterBase.__init__(self, structure)
        self.type = ChannelType(self.type)


class MarkerEvent(_ConverterBase):
    """Describes one marker event"""
    source = None
    type = None
    time = None
    text = None

    def __init__(self, structure: "DmdMarkerEvent"):
        _ConverterBase.__init__(self, structure)
        self.source = MarkerEventSource(self.source)
        self.type = MarkerEventType(self.type)


class Sweep(_ConverterBase):
    """Describes a single sweep of data"""
    first_sample = None
    last_sample = None
    start_time = None
    end_time = None
    sample_frequency = None

    @property
    def max_samples(self):
        """Calculated max samples"""
        return self.last_sample - self.first_sample + 1

    def __init__(self, structure: "DmdSweep"):
        _ConverterBase.__init__(self, structure)

@total_ordering
class Version:
    """Version information with major and minor part"""
    major = None
    minor = None
    micro = None

    def __init__(self, major, minor, micro = 0):
        self.major = major
        self.minor = minor
        self.micro = micro

    def __repr__(self):
        return f"{self.__class__.__name__} (major: {self.major}, minor: {self.minor}, micro: {self.micro})"

    def __str__(self):
        if self.micro > 0:
            return f"{self.major}.{self.minor}.{self.micro}"
        return f"{self.major}.{self.minor}"

    def supports(self, ma, mi):
        return self.major == ma and self.minor >= mi

    def __eq__(self, o):
        return self.major == o.major and self.minor == o.minor and self.micro == o.micro

    def __ne__(self, o):
        return self.major != o.major or self.minor != o.minor or self.micro != o.micro

    def __lt__(self, o):
        if self.major < o.major:
            return True
        if self.major > o.major:
            return False
        if self.minor < o.minor:
            return True
        if self.minor > o.minor:
            return False
        return self.micro < o.micro
