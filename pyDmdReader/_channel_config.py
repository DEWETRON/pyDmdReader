"""
Copyright DEWETRON GmbH 2019

Dmd reader library - Channel configuration module
"""


from .types import SampleType


class ChannelConfig:
    """Channel configuraation class"""
    name = None
    sample_rate = None
    type = None
    unit = None
    description = None
    measurement_duration = None
    range_min = None
    range_max = None
    handle = None
    raw_sample_type = None
    reduced_sample_type = None
    max_sample_dimension = None
    sweeps = []
    reduced_sweeps = []

    def __init__(self, channel_info, channel_handle):
        self.__dict__.update(channel_info.__dict__)
        self.handle = channel_handle

    @property
    def dtype(self) -> str:
        """Get the numpy dtype according to sample_type"""
        if self.raw_sample_type == SampleType.DOUBLE:
            return "float64"
        elif self.raw_sample_type == SampleType.SINT32:
            return "i4"
        elif self.raw_sample_type == SampleType.DOUBLE_VECTOR:
            return "float64"
        elif self.raw_sample_type == SampleType.COMPLEX_VECTOR:
            return "complex128"
        return ""

    def __str__(self):
        return "{} ({} Hz) - {}".format(self.name, self.sample_rate, self.type)
