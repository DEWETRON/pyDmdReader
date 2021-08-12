"""
Copyright DEWETRON GmbH 2019-2021

DMD reader library - Main class
"""

import numpy as np
import pandas as pd
from enum import Enum
from . import _api
from .types import ChannelType, SampleType, DataFrameColumn
from .data_types import HeaderField, MarkerEvent, Version
from ._channel_config import ChannelConfig
from typing import List, Dict, Tuple

class TimestampFormat(Enum):
    """Specification of all possible timestamp formats"""
    NONE = 0
    SECONDS_SINCE_START = 1
    ABSOLUTE_LOCAL_TIME = 2
    ABSOLUTE_UTC_TIME = 3

class DmdReader:
    """Dmd reader class"""
    def __init__(self, file_name):
        """
        Load data file with file_name and retrieve channel informations
        This works only for unique channel names, otherwise they get overwitten
        """
        self.__file_handle = self.__load_file(file_name)
        self.measurement_start_time_utc = _api.get_measurement_start_time(self.__file_handle, utc=True).datetime
        self.measurement_start_time_local = _api.get_measurement_start_time(self.__file_handle, utc=False).datetime
        self.__channels = self.__get_channel_infos()

    def close(self) -> None:
        """Close DMD file"""
        _api.close_file(self.__file_handle)

    def __gather_usable_channels(self, ch_names):
        if type(ch_names) is str:
            ch_names = [ch_names] # convert single channel to list

        used_channels = []
        sample_rate = None
        for ch_name in ch_names:
            self.__check_channel(ch_name)
            ch_config = self.__channels[ch_name]

            if ch_config.raw_sample_type != SampleType.INVALID:
                used_channels.append(ch_name)
            
            if sample_rate is None:
                sample_rate = ch_config.sample_rate
            else:
                if sample_rate != ch_config.sample_rate:
                    raise RuntimeError("All requested channels need to have the same sample rate")

        return used_channels

    def read_dataframe(self,
        ch_names,
        start_time:float = 0,
        end_time:float = None,
        timestamp_format: TimestampFormat = TimestampFormat.SECONDS_SINCE_START
    ) -> pd.DataFrame:
        """
        Read all data from specified channels (single name or list of names).
        Each channel will be stored in a column of a pandas DataFrame with a common timestamp index.
        By specifying the inclusive time-range [start_time, end_time] in seconds since recording start, only samples within that inverval are returned
        By default timestamps in seconds relative to recording start are returned:
            - TimestampFormat.NONE -> no timestamp information is stored in the data frame
            - TimestampFormat.ABSOLUTE_UTC_TIME -> relative timestamps are replaced with absolute utc timezone timestamps
            - TimestampFormat.ABSOLUTE_LOCAL_TIME -> relative timestamps are replaced with absolute local recorded timezone timestamps
        """

        used_channels = self.__gather_usable_channels(ch_names)

        if len(used_channels) == 0:
            return pd.DataFrame()

        data_frame = None
        for ch_name in used_channels:
            ch_config = self.__channels[ch_name]

            if start_time == 0 and end_time == None:
                # All sweeps
                timestamps, data = self.__get_all_sweeps(ch_config)
            else:
                actual_end_time = end_time if end_time is not None else ch_config.sweeps[-1].end_time

                timestamps = np.array([], dtype='float64')
                data = np.array([])
                
                # Get data from suitable sweeps
                for sweep in ch_config.sweeps:
                    if sweep.start_time <= actual_end_time and sweep.end_time >= start_time:
                        if sweep.sample_frequency != 0:
                            # Sync channel
                            start_sample = int(start_time * sweep.sample_frequency)
                            end_sample = int(actual_end_time * sweep.sample_frequency)
                            first_sample, max_samples = self.__get_corrected_sample_count(sweep, start_sample, end_sample)

                            sweep_timestamps, sweep_data, *_ = self.__get_single_sweep(ch_config, first_sample, max_samples)
                            timestamps = np.r_[timestamps, sweep_timestamps]
                            data = np.r_[data, sweep_data]
                        else:
                            raise NotImplementedError("Async channels are not yet supported with timeranges")
            
            if data_frame is None:
                if timestamp_format == TimestampFormat.NONE:
                    data_frame = pd.DataFrame()
                else:
                    data_frame = pd.DataFrame(index=timestamps)
            else:
                if timestamp_format != TimestampFormat.NONE and not np.array_equal(data_frame.index, timestamps):
                    raise RuntimeError("Cannot combine channels with different timestamps. Try fetching data for each channel individually.")

            if ch_config.max_sample_dimension == 1:
                data_frame[ch_name] = data
            else:
                if ch_config.max_sample_dimension == len(data):
                    columns = ["{}[{}]".format(ch_name, i) for i in range(0, ch_config.max_sample_dimension)]

                    #TODO: This code is untested
                    raise NotImplemented("The following code has not been tested and therefore raises an exception for now")
                    data = data.reshape(1, ch_config.max_sample_dimension)
                    if timestamp_format == TimestampFormat.NONE:
                        data_frame = pd.DataFrame(data=data, columns=columns)
                    else:
                        timestamps = timestamps.reshape(1, len(timestamps))
                        data_frame = pd.DataFrame(index=timestamps, data=data, columns=columns)

                    #new_data = np.concatenate((timestamps, data), axis=1)
                    #new_data = new_data.reshape(1, ch_config.max_sample_dimension + 1)
                    #data_frame = pd.DataFrame(new_data, columns=columns)
                else:
                    if data_frame is None:
                        data_frame = pd.DataFrame(index=timestamps)
                    for i in range(0, ch_config.max_sample_dimension):
                        data_frame["{}[{}]".format(ch_name, i)] = data[i::ch_config.max_sample_dimension]

        if (timestamp_format == TimestampFormat.ABSOLUTE_LOCAL_TIME or
            timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME):
            data_frame = self.__get_data_abs_timestamp_pandas(data_frame, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME)

        return data_frame
    
    def read_array(self,
        ch_names,
        sweep_no=None,
        first_sample: int=None, max_samples: int=None,
        timestamp_format: TimestampFormat = TimestampFormat.SECONDS_SINCE_START
    ) -> Tuple[np.array, np.array]:
        """
        Read all data from specified channels (single name or list of names).
        Each channel will be stored in a row of a numpy data array. A separate timestamp array will contain the timestamps.
        If a sweep_no is given, only this is sweep is read.
        If sweep_no is None, first_sample and max_samples are ignored
        By default timestamps in seconds relative to recording start are returned:
            - TimestampFormat.NONE -> no timestamp information is stored in the data frame
            - TimestampFormat.ABSOLUTE_UTC_TIME -> relative timestamps are replaced with absolute utc timezone timestamps
            - TimestampFormat.ABSOLUTE_LOCAL_TIME -> relative timestamps are replaced with absolute local recorded timezone timestamps
        """
        used_channels = self.__gather_usable_channels(ch_names)

        if len(used_channels) == 0:
            return None, None
        
        result = np.array([])
        result_timestamps = None
        for ch_name in used_channels:
            ch_config = self.__channels[ch_name]

            if sweep_no is None:
                # All sweeps
                timestamps, data = self.__get_all_sweeps(ch_config)
            else:
                # Single sweep
                self.__check_sweep_number(ch_config, sweep_no)

                sweep = ch_config.sweeps[sweep_no]
                first_sample_corrected, max_samples_corrected = self.__get_corrected_sample_count(sweep, first_sample, max_samples)

                # Only for Sync Channels
                if ch_config.sample_rate == 0:
                    # HINT: sample_rate == 0 -> Async channel
                    # TODO: Single sweep not for async channels
                    return None, None
                timestamps, data, *_ = self.__get_single_sweep(ch_config, first_sample_corrected, max_samples_corrected)

            if result_timestamps is None:
                if timestamp_format != TimestampFormat.NONE:
                    result_timestamps = timestamps
            else:
                if timestamp_format != TimestampFormat.NONE and not np.array_equal(result_timestamps, timestamps):
                    raise RuntimeError("Cannot combine channels with different timestamps. Try fetching data for each channel individually.")

            if ch_config.max_sample_dimension == 1:
                if len(result) == 0:
                    result = data
                else:
                    result = np.vstack([result, data])
            else:
                for i in range(0, ch_config.max_sample_dimension):
                    if len(result) == 0:
                        result = data[i::ch_config.max_sample_dimension]
                    else:
                        result = np.vstack([result, data[i::ch_config.max_sample_dimension]])

        if (timestamp_format == TimestampFormat.ABSOLUTE_LOCAL_TIME or
            timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME):
            result_timestamps = self.__get_data_abs_timestamp_array(result_timestamps, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME)

        return result, result_timestamps

    def read_reduced(self, ch_name, timestamp_format = TimestampFormat.SECONDS_SINCE_START) -> pd.DataFrame:
        """
        Read the reduced data from the given channel

        Returned DataFrame columns: timestamps, min, max, avg, rms
        """
        self.__check_channel(ch_name)
        ch_config = self.__channels[ch_name]
        data = np.array([], dtype="float64")
        timestamps = np.array([], dtype="float64")

        if ch_config.reduced_sample_type == SampleType.INVALID:
            return pd.DataFrame()
        elif ch_config.reduced_sample_type == SampleType.REDUCED:
            for sweep in ch_config.reduced_sweeps:
                (
                    num_valid_samples,
                    next_reduced_sample,
                    reduced_values,
                    reduced_timestamps
                ) = _api.get_samples_and_ts_reduced_value_seconds(
                    ch_config.handle,
                    sweep.first_sample,
                    sweep.max_samples
                )
                timestamps = np.r_[timestamps, np.frombuffer(reduced_timestamps, count=num_valid_samples)]
                data = np.r_[data, np.frombuffer(reduced_values, count=4*num_valid_samples)]

            if timestamp_format == TimestampFormat.NONE:
                data_frame = pd.DataFrame(dtype="float64")
            else:
                data_frame = pd.DataFrame(index=timestamps, dtype="float64")
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_MIN] = data[0::4]
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_MAX] = data[1::4]
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_AVG] = data[2::4]
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_RMS] = data[3::4]

            if timestamp_format == TimestampFormat.ABSOLUTE_LOCAL_TIME or timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME:
                data_frame = self.__get_data_abs_timestamp_pandas(data_frame, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME)

            return data_frame
        else:
            raise NotImplementedError("Sampletype {} not supported for reduced data".format(ch_config.reduced_sample_type))

    @property
    def channels(self):
        """Channel definitions"""
        return self.__channels

    @property
    def channel_names(self):
        """Alphabetically sorted list of channel names"""
        return sorted(self.__channels.keys())

    @property
    def headers(self) -> List[HeaderField]:
        """Read the Header Entries"""
        num_header_fields = _api.get_num_header_fields(self.__file_handle)
        return _api.get_header_fields(self.__file_handle, 0, num_header_fields)

    @property
    def markers(self) -> List[MarkerEvent]:
        """Get all available markers"""
        num_markers = _api.get_num_markers(self.__file_handle)
        return _api.get_markers(self.__file_handle, 0, num_markers)

    @property
    def version(self) -> Version:
        """Get dmd reader dll version"""
        return _api.get_version()

    def __get_channel_infos(self) -> Dict[str, ChannelConfig]:
        """Read all channel infos"""
        channels = {}
        channel_type = ChannelType.ALL_CHANNELS
        for ch_idx in range(0, _api.get_num_channels(self.__file_handle, ChannelType.ALL_CHANNELS)):
            channel_handle, ret_num_channels = _api.get_channels(self.__file_handle, channel_type, ch_idx, 1)
            channel_info = _api.get_channel_information(channel_handle)
            ch_config = ChannelConfig(channel_info, channel_handle)

            (
                ch_config.raw_sample_type,
                ch_config.reduced_sample_type,
                ch_config.max_sample_dimension
            ) = _api.get_vector_sample_types(ch_config.handle)

            # Read sweep settings
            num_sweeps = _api.get_num_data_sweeps(channel_handle)
            if num_sweeps > 0:
                ch_config.sweeps = _api.get_data_sweeps(channel_handle, 0, num_sweeps)

            # Read reduced sweep settings
            num_reduced_sweeps = _api.get_num_reduced_sweeps(channel_handle)
            if num_reduced_sweeps > 0:
                ch_config.reduced_sweeps = _api.get_reduced_sweeps(channel_handle, 0, num_reduced_sweeps)

            if ch_config.name in channels:
                raise KeyError("Duplicate channel name: {}".format(ch_config.name))

            channels[ch_config.name] = ch_config
        return channels

    def __check_channel(self, ch_name) -> None:
        """Check if given ch_name is available"""
        if ch_name not in self.__channels:
            raise KeyError("No channel with given name ({}) can be found".format(ch_name))

    def __get_all_sweeps(self, ch_config) -> Tuple[np.ndarray, np.ndarray]:
        """Get data from all sweeps of given ch_name"""
        data = np.array([], dtype=ch_config.dtype)
        timestamps = np.array([], dtype="float64")
        block_size = int(1e6)

        for sweep in ch_config.sweeps:
            first_sample = sweep.first_sample

            # HINT: Splitting up blocks is needed for async channels to reduce memory allocation
            while True:
                if sweep.last_sample - first_sample + 1 >= block_size:
                    max_samples = block_size
                else:
                    max_samples = sweep.last_sample - first_sample + 1

                raw_timestamps, raw_values, next_sample = self.__get_single_sweep(ch_config, first_sample, max_samples)
                data = np.r_[data, raw_values]
                timestamps = np.r_[timestamps, raw_timestamps]

                if next_sample > sweep.last_sample:
                    break
                first_sample = next_sample

        return timestamps, data

    @staticmethod
    def __get_single_sweep(ch_config, first_sample, max_samples) -> Tuple[np.ndarray, np.ndarray, int]:
        """Get data for given sweep of given channel"""
        timestamps_dtype = "float64"
        if ch_config.raw_sample_type == SampleType.DOUBLE:
            num_valid_samples, next_sample, raw_values, raw_timestamps = _api.get_samples_and_ts_scaled_value_seconds(
                ch_config.handle,
                first_sample,
                max_samples
            )
        elif ch_config.raw_sample_type == SampleType.SINT32:
            # Digital
            num_valid_samples, next_sample, raw_values, raw_timestamps = _api.get_samples_and_ts_digital_value_seconds(
                ch_config.handle,
                first_sample,
                max_samples
            )
        elif ch_config.raw_sample_type == SampleType.DOUBLE_VECTOR:
            num_valid_samples, next_sample, raw_values, raw_timestamps = _api.get_samples_and_ts_scalar_vector_seconds(
                ch_config.handle,
                first_sample,
                max_samples,
                ch_config.max_sample_dimension
            )
        elif ch_config.raw_sample_type == SampleType.COMPLEX_VECTOR:
            num_valid_samples, next_sample, raw_values, raw_timestamps = _api.get_samples_and_ts_complex_vector_seconds(
                ch_config.handle,
                first_sample,
                max_samples,
                ch_config.max_sample_dimension
            )
        else:
            raise NotImplementedError("Sampletype {} not supported".format(ch_config.raw_sample_type))

        timestamps = np.frombuffer(raw_timestamps, dtype=timestamps_dtype, count=num_valid_samples)
        data = np.frombuffer(raw_values, dtype=ch_config.dtype, count=num_valid_samples*ch_config.max_sample_dimension)

        return timestamps, data, next_sample

    @staticmethod
    def __get_corrected_sample_count(sweep, start_sample, end_sample = None) -> Tuple[int, int]:
        """Get a corrected first_sample and max_sample value"""

        # TODO: This is a hack, is there a better way to find out the start-offset
        start_offset = int(sweep.first_sample - sweep.start_time * sweep.sample_frequency)

        start_sample = start_sample + start_offset
        if end_sample is not None:
            end_sample = end_sample + start_offset

        if start_sample < sweep.first_sample:
            start_sample = sweep.first_sample
        if end_sample is None or end_sample > sweep.last_sample:
            end_sample = sweep.last_sample
        return start_sample, end_sample - start_sample + 1

    @staticmethod
    def __check_sweep_number(ch_config, sweep_no) -> None:
        """Check if given sweep number is valid for given ch_config"""
        if not(0 <= sweep_no < len(ch_config.sweeps)):
            raise IndexError("Selected sweep number {} not valid. Valid range: 0 .. {}".format(
                sweep_no, len(ch_config.sweeps)-1)
            )

    @staticmethod
    def __load_file(file_name):
        """Open the dmd file"""
        return _api.open_file(file_name)

    def __get_data_abs_timestamp_pandas(self, data_frame, utc=True) -> pd.DataFrame:
        """Convert Timestamp column to absolute timestamps"""
        start_time = self.measurement_start_time_utc if utc else self.measurement_start_time_local
        data_frame.index = start_time + pd.to_timedelta(data_frame.index, unit='s')
        return data_frame
    
    def __get_data_abs_timestamp_array(self, timestamps, utc=True) -> np.array:
        """Convert Timestamp column to absolute timestamps"""
        start_time = self.measurement_start_time_utc if utc else self.measurement_start_time_local
        start_time_np = (start_time + start_time.utcoffset()).to_datetime64()
        timestamps = start_time_np + np.timedelta64(1, 's') * timestamps
        return timestamps
