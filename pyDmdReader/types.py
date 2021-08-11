"""
Copyright DEWETRON GmbH 2019

Dmd reader library - Module for all available enums
"""


from enum import Enum
from typing import List


class ErrorCode(Enum):
    """Specification of all the possible error codes returned by the dmd reader api interface."""
    NO_ERROR = 0
    FILE_DOES_NOT_EXIST = -5001
    FILE_INVALID = -5002
    INTERNAL_ERROR = -5003
    INVALID_ARGUMENT = -5004
    INVALID_FILE_HANDLE = -5005
    INVALID_CHANNEL_HANDLE = -5006
    INVALID_MEMORY_SIZE = -5007
    MAXIMUM_NUMBER_OF_DATA_VALUES_EXCEEDED = -5008
    CHANNEL_DATA_TYPE_MISMATCH = -5009
    INVALID_MARKER_HANDLE = -5010
    OUT_OF_MEMORY = -5011
    INCOMPATIBLE_VERSION = -5012
    API_NOT_INITIALIZED = -5013
    INPUT_BUFFER_TOO_SMALL = -5014
    ERROR_END = -8000


class SampleType(Enum):
    """Specification of all possible sample types of the channel data."""
    INVALID = 0
    DOUBLE = 1
    REDUCED = 2
    SINT32 = 3
    DOUBLE_VECTOR = 100
    COMPLEX_VECTOR = 101


class ChannelType(Enum):
    """Specification of all possible channel types."""
    ALL_CHANNELS = 0
    ANALOG_CHANNEL = 1
    COUNTER_CHANNEL = 2
    DIGITAL_CHANNEL = 3


class MarkerEventSource(Enum):
    """Specification of all possible marker event sources."""
    SOURCE_TRIGGER = 0
    SOURCE_APPLICATION = 1
    SOURCE_MANUAL = 2
    SOURCE_EXTERNAL = 3
    SOURCE_SYNC = 4
    SOURCE_TOPOLOGY = 5


class MarkerEventType(Enum):
    """Specification of all possible marker event types."""
    MARKER = 0
    START = 1
    STOP = 2
    NODE_RECORDING_STOP = 3
    PRETIME_START = 4
    POSTTIME_STOP = 5
    SYNC_SIGNAL_LOST = 6
    SYNC_TIME_ERROR = 7
    SYNC_SYNC_LOST = 8
    SYNC_SYNC_ERROR = 9
    SYNC_RESYNCED = 10
    TOPOLOGY_NODE_FOUND = 11
    TOPOLOGY_NODE_LOST = 12
    ALARM = 13
    ALARM_ACK = 14
    EVENT = 15
    SPLIT_START = 16
    SPLIT_STOP = 17
    DATA_DELAY_NORMAL = 18
    DATA_DELAY_WARNING = 19
    DATA_DELAY_ERROR = 20


class DataFrameColumn:
    """All accessible DataFrame columns are in uppercase to avoid shadowing built-in names"""
    DATA_FRAME_COLUMN_MESSAGE_ID = "MESSAGE_ID"
    DATA_FRAME_COLUMN_MESSAGE_EXTENDED = "MESSAGE_EXTENDED"
    DATA_FRAME_COLUMN_REDUCED_MIN = "MIN"
    DATA_FRAME_COLUMN_REDUCED_MAX = "MAX"
    DATA_FRAME_COLUMN_REDUCED_AVG = "AVG"
    DATA_FRAME_COLUMN_REDUCED_RMS = "RMS"

    @classmethod
    def getReducedColumns(cls) -> List[str]:
        """Get a list of all reduced column names"""
        return [
            cls.DATA_FRAME_COLUMN_REDUCED_AVG,
            cls.DATA_FRAME_COLUMN_REDUCED_MAX,
            cls.DATA_FRAME_COLUMN_REDUCED_MIN,
            cls.DATA_FRAME_COLUMN_REDUCED_RMS,
        ]
