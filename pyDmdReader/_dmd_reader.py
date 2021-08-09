"""
Copyright DEWETRON GmbH 2019-2021

DMD reader library - Main class
"""

import numpy as np
import pandas as pd
import datetime
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

class DmdReader(DataFrameColumn):
    """Dmd reader class"""
    def __init__(self, file_name):
        """
        Load data file with file_name and create member with channel informations.
        This works only for unique channel names, otherwise they get overwitten
        """
        self.__file_handle = self.__load_file(file_name)
        self.measurement_start_time_utc = _api.get_measurement_start_time(self.__file_handle, utc=True).datetime
        self.measurement_start_time_local = _api.get_measurement_start_time(self.__file_handle, utc=False).datetime
        self.channels = self.__get_channel_infos()
        self.channel_names = sorted(self.channels.keys())

    def get_data(self,
        ch_name,
        sweep_no=None,
        first_sample=None, max_samples=None,
        timestamp_format = TimestampFormat.SECONDS_SINCE_START
    ) -> pd.DataFrame:
        """
        Read all data from specified channel. If sweep is given, only this is read.
        If sweep_no is None, first_sample and max_samples are ignored
        By default timestamps relative to recording start are returned:
            - TimestampFormat.ABSOLUTE_UTC_TIME -> relative timestamps are replaced with absolute utc timezone timestamps
            - TimestampFormat.ABSOLUTE_LOCAL_TIME -> relative timestamps are replaced with absolute local recorded timezone timestamps
        """
        self.__check_channel(ch_name)
        ch_config = self.channels[ch_name]

        if ch_config.raw_sample_type == SampleType.INVALID:
            return pd.DataFrame()

        if sweep_no is None:
            # All sweeps
            timestamps, data = self.__get_all_sweeps(ch_config)
        else:
            # Single sweep
            self.__check_sweep_number(ch_config, sweep_no)

            sweep = ch_config.sweeps[sweep_no]
            first_sample, max_samples = self.__get_corrected_sample_count(sweep, first_sample, max_samples)

            # Only for Sync Channels
            if ch_config.sample_rate == 0:
                # HINT: sample_rate == 0 -> Async channel
                # TODO: Single sweep not for async channels
                return pd.DataFrame()
            timestamps, data, *_ = self.__get_single_sweep(ch_config, first_sample, max_samples)

        if ch_config.max_sample_dimension != 1:
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
                data_frame = pd.DataFrame(index=timestamps)
                for i in range(0, ch_config.max_sample_dimension):
                    data_frame["{}[{}]".format(ch_name, i)] = data[i::ch_config.max_sample_dimension]
        else:
            if timestamp_format == TimestampFormat.NONE:
                data_frame = pd.DataFrame(data=data, columns=[ch_name])
            else:
                data_frame = pd.DataFrame(index=timestamps, data=data, columns=[ch_name])

        if (timestamp_format == TimestampFormat.ABSOLUTE_LOCAL_TIME or
            timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME):
            data_frame = self.__get_data_abs_timestamp(data_frame, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME)

        return data_frame

    def get_reduced_data(self, ch_name, timestamp_format = TimestampFormat.SECONDS_SINCE_START) -> pd.DataFrame:
        """
        Read the reduced data from the given channel

        Returned DataFrame columns: timestamps, min, max, avg, rms
        """
        self.__check_channel(ch_name)
        ch_config = self.channels[ch_name]
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

            data_frame = pd.DataFrame(
                index=timestamps,
                columns={
                    self.DATA_FRAME_COLUMN_REDUCED_MIN: data[0::4],
                    self.DATA_FRAME_COLUMN_REDUCED_MAX: data[1::4],
                    self.DATA_FRAME_COLUMN_REDUCED_AVG: data[2::4],
                    self.DATA_FRAME_COLUMN_REDUCED_RMS: data[3::4],
            })

            if timestamp_format == TimestampFormat.ABSOLUTE_LOCAL_TIME or timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME:
                data_frame = self.__get_data_abs_timestamp(data_frame, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME)

            return data_frame
        else:
            raise NotImplementedError("Sampletype {} not supported for reduced data".format(ch_config.reduced_sample_type))

    def get_header(self) -> List[HeaderField]:
        """Read the Header Entries"""
        num_header_fields = _api.get_num_header_fields(self.__file_handle)
        return _api.get_header_fields(self.__file_handle, 0, num_header_fields)

    def get_markers(self) -> List[MarkerEvent]:
        """Get all available markers"""
        num_markers = _api.get_num_markers(self.__file_handle)
        return _api.get_markers(self.__file_handle, 0, num_markers)

    def close(self) -> None:
        """Close DMD file"""
        _api.close_file(self.__file_handle)

    @staticmethod
    def get_version() -> Version:
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
        if ch_name not in self.channels:
            raise KeyError("No channel with given name ({}) can be found".format(ch_name))

    def __get_all_sweeps(self, ch_config) -> Tuple[np.ndarray, np.ndarray]:
        """Get data from all sweeps of given ch_name"""
        data = np.array([], dtype=ch_config.dtype)
        timestamps = np.array([], dtype="float64")

        for sweep in ch_config.sweeps:
            first_sample = sweep.first_sample
            block_size = int(1e6)
            # HINT: Splitting up blocks is needed for asnyc channels to reduce memory allocation
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
    def __get_corrected_sample_count(sweep, first_sample, max_samples) -> Tuple[int, int]:
        """Get a corrected first_sample and max_sample value"""
        if max_samples is None:
            max_samples = sweep.max_samples

        if first_sample is None:
            first_sample = sweep.first_sample
        else:
            if first_sample > max_samples:
                raise IndexError("Given first_sample ({}) is greater than max. available samples ({})".format(
                    first_sample, max_samples)
                )
            # HINT: Within the dmd file, samples are counted from acquisition start not recording start
            first_sample += sweep.first_sample

        if sweep.last_sample - first_sample + 1 < max_samples:
            raise IndexError("Amount of requested samples ({}) is greater than max. available samples ({})".format(
                max_samples, sweep.last_sample-first_sample+1)
            )
        return first_sample, max_samples

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

    def __get_data_abs_timestamp(self, data_frame, utc=True) -> pd.DataFrame:
        """Convert Timestamp column to absolute timestamps"""
        start_time = self.measurement_start_time_utc if utc else self.measurement_start_time_local
        data_frame.index = [start_time + datetime.timedelta(seconds=sec) for sec in data_frame.index]
        return data_frame
