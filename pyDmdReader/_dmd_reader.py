"""
Copyright DEWETRON GmbH 2021

DMD reader library - Main class
"""


import xml.etree.ElementTree as et
import numpy as np
import pandas as pd
from numpy import ndarray

from . import _api
from .types import ChannelType, SampleType, DataFrameColumn, TimestampFormat
from .data_types import HeaderField, MarkerEvent, MarkerEventType, MarkerEventSource, Version
from ._channel_config import ChannelConfig
from ._structures import DmdSampleValueComplex, DmdSampleValueReduced
from ctypes import c_double, c_int32
from typing import List, Dict, Tuple, Union, Optional, TYPE_CHECKING

ASYNC_BLOCK_SIZE = 1000000
if TYPE_CHECKING:
    from .data_types import Sweep
    from ctypes import c_void_p


class DmdReader:
    """Dmd reader class"""
    def __init__(self, file_name: str):
        """
        Load data file with file_name and retrieve channel informations

        Retrieve a list of channel ids (`channel_ids`) or names (`channel_names`)
        and request data from selected channels via `read_dataframe`, `read_array` or `read_reduced`
        Channels with a unique name can be accessed via channel names
        """
        self.__file_handle = self.__load_file(file_name)
        self.measurement_start_time_utc = _api.get_measurement_start_time(self.__file_handle, utc=True).datetime
        self.measurement_start_time_local = _api.get_measurement_start_time(self.__file_handle, utc=False).datetime
        self.__channels = self.__get_channel_infos()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @property
    def channels(self) -> Dict[str, ChannelConfig]:
        """
        Channel definitions with the channel name as key
        @raise KeyError: if duplicate names are found
        """
        result = {}
        for _, channel in self.__channels.items():
            if channel.name in result:
                raise KeyError(f"Duplicate channel name: {channel.name}")
            result[channel.name] = channel

        return result

    @property
    def allchannels(self) -> Dict[int, ChannelConfig]:
        """Channel definitions with a unique channel id as key"""
        return self.__channels

    @property
    def channel_names(self) -> List[str]:
        """Alphabetically sorted list of channel names (including duplicates)"""
        return sorted([ch.name for key, ch in self.__channels.items()])

    @property
    def channel_ids(self) -> List[int]:
        """List of all channel ids"""
        return list(self.__channels.keys())

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
    def measurement_duration(self) -> float:
        """Get the duration of the measurement in seconds"""
        for marker in self.markers:
            if marker.source == MarkerEventSource.SOURCE_MANUAL and marker.type == MarkerEventType.STOP:
                return marker.time

        raise RuntimeError("Cannot determine the length of the measurement")

    @property
    def configuration_xml(self) -> str:
        """Get the configuration to the dmd"""
        config = _api.get_configuration_xml(self.__file_handle)
        return config.decode("utf-8")

    @property
    def configuration_etree(self) -> str:
        """Get the configuration to the dmd"""
        config = self.configuration_xml
        return et.fromstring(config)

    @property
    def version(self) -> Version:
        """Get dmd reader dll version"""
        return _api.get_version()

    def close(self) -> None:
        """Close DMD file"""
        _api.close_file(self.__file_handle)

    def read_dataframe(
        self,
        ch_names: Union[List[str], str, List[int], int],
        start_time: float = 0.0,
        end_time: Optional[float] = None,
        timestamp_format: TimestampFormat = TimestampFormat.SECONDS_SINCE_START,
        max_samples: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Read all data from specified channels (single name/id or list of names/ids).
        Each channel will be stored in a column of a pandas DataFrame with a common timestamp index.
        By specifying the inclusive time-range [`start_time`, `end_time`] in seconds since recording start, only samples
        within that interval are returned.
        The number of returned samples can be limited by the `max_samples` parameter.

        By default, timestamps in seconds relative to recording start are returned.
        This can be changed by the `timestamp_format` parameter:
            - TimestampFormat.NONE -> no timestamp information is stored in the data frame
            - TimestampFormat.ABSOLUTE_UTC_TIME -> relative timestamps are replaced with absolute utc timezone
              timestamps
            - TimestampFormat.ABSOLUTE_LOCAL_TIME -> relative timestamps are replaced with absolute local recorded
              timezone timestamps
        """
        used_channels = self.__gather_usable_channels(ch_names)

        if not used_channels:
            return pd.DataFrame()

        data_frames = []
        for ch_name in used_channels:
            ch_config = self.__channels[ch_name]

            if start_time == 0.0 and end_time is None:
                timestamps, data = self.__get_all_sweeps(ch_config, max_samples)
            else:
                timestamps, data = self.__get_ranged_sweeps(ch_config, start_time, end_time, max_samples)

            if timestamp_format == TimestampFormat.NONE:
                timestamps = None

            if ch_config.max_sample_dimension == 1:
                columns = [ch_config.name]
            else:
                data = data.reshape(-1, ch_config.max_sample_dimension)
                columns = [f"{ch_config.name}[{i}]" for i in range(0, ch_config.max_sample_dimension)]

            data_frames.append(pd.DataFrame(data, index=timestamps, columns=columns))

        full_frame = pd.concat(data_frames, axis=1)

        if timestamp_format in [
            TimestampFormat.ABSOLUTE_LOCAL_TIME,
            TimestampFormat.ABSOLUTE_UTC_TIME,
        ]:
            full_frame = self.__get_data_abs_timestamp_pandas(
                full_frame, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME
            )
        return full_frame

    def read_array(
        self,
        ch_names: Union[List[str], str, List[int], int],
        start_time: float = 0.0,
        end_time: Optional[float] = None,
        timestamp_format: TimestampFormat = TimestampFormat.SECONDS_SINCE_START,
        max_samples: Optional[int] = None
    ) -> Tuple[Optional[np.array], Optional[np.array]]:
        """
        Read all data from specified channels (single name/id or list of names/ids).
        Each channel will be stored in a row of a numpy data array. A separate timestamp array will contain the
        timestamps.
        By specifying the inclusive time-range [`start_time`, `end_time`] in seconds since recording start, only samples
        within that interval are returned.
        The number of returned samples can be limited by the `max_samples` parameter.

        By default, timestamps in seconds relative to recording start are returned.
        This can be changed by the `timestamp_format` parameter:
            - TimestampFormat.NONE -> no timestamp information is stored in the data frame
            - TimestampFormat.ABSOLUTE_UTC_TIME -> relative timestamps are replaced with absolute utc timezone
              timestamps
            - TimestampFormat.ABSOLUTE_LOCAL_TIME -> relative timestamps are replaced with absolute local recorded
              timezone timestamps
        """
        used_channels = self.__gather_usable_channels(ch_names)

        if not used_channels:
            return None, None

        result_list = []
        result_timestamps = None
        for ch_name in used_channels:
            ch_config = self.__channels[ch_name]

            if start_time == 0.0 and end_time is None:
                timestamps, data = self.__get_all_sweeps(ch_config, max_samples)
            else:
                timestamps, data = self.__get_ranged_sweeps(ch_config, start_time, end_time, max_samples)

            result_timestamps = self.__parse_timestamps(result_timestamps, timestamp_format, timestamps)
            self.__update_result_list(ch_config, data, result_list)
            result = np.array(result_list)

        result_timestamps = self.__parse_utc_timestamps(result_timestamps, timestamp_format)

        if len(result) == 1:
            result = result[0]

        return result, result_timestamps

    def read_array_by_index(
        self,
        ch_names: Union[List[str], str, List[int], int],
        start_sample: int = 0,
        end_sample: Optional[int] = None,
        timestamp_format: TimestampFormat = TimestampFormat.SECONDS_SINCE_START
    ) -> Tuple[Optional[np.array], Optional[np.array]]:
        """
        Read all data from specified channels (single name/id or list of names/ids).
        Each channel will be stored in a row of a numpy data array. A separate timestamp array will contain the
        timestamps.
        By specifying the inclusive sample-range [`start_sample`, `end_sample`], only samples within that interval are returned.

        By default, timestamps in seconds relative to recording start are returned.
        This can be changed by the `timestamp_format` parameter:
            - TimestampFormat.NONE -> no timestamp information is stored in the data frame
            - TimestampFormat.ABSOLUTE_UTC_TIME -> relative timestamps are replaced with absolute utc timezone
              timestamps
            - TimestampFormat.ABSOLUTE_LOCAL_TIME -> relative timestamps are replaced with absolute local recorded
              timezone timestamps
        """
        used_channels = self.__gather_usable_channels(ch_names)

        if not used_channels:
            return None, None

        result_list = []
        result_timestamps = None
        for ch_name in used_channels:
            ch_config = self.__channels[ch_name]

            if start_sample == 0 and end_sample is None:
                timestamps, data = self.__get_all_sweeps(ch_config)
            else:
                timestamps, data = self.__get_ranged_sweeps_by_index(ch_config, start_sample, end_sample)

            result_timestamps = self.__parse_timestamps(result_timestamps, timestamp_format, timestamps)
            self.__update_result_list(ch_config, data, result_list)
            result = np.array(result_list)

        result_timestamps = self.__parse_utc_timestamps(result_timestamps, timestamp_format)

        if len(result) == 1:
            result = result[0]

        return result, result_timestamps

    def __parse_utc_timestamps(self, result_timestamps: ndarray, timestamp_format:TimestampFormat):
        if timestamp_format in [
            TimestampFormat.ABSOLUTE_LOCAL_TIME,
            TimestampFormat.ABSOLUTE_UTC_TIME,
        ]:
            result_timestamps = self.__get_data_abs_timestamp_array(
                result_timestamps, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME
            )
        return result_timestamps

    @staticmethod
    def __update_result_list(ch_config: ChannelConfig, data: ndarray, result_list: List[ndarray]):
        if ch_config.max_sample_dimension == 1:
            result_list.append(data)
        else:
            for i in range(0, ch_config.max_sample_dimension):
                result_list.append(data[i::ch_config.max_sample_dimension])

    @staticmethod
    def __parse_timestamps(result_timestamps: Optional[ndarray], timestamp_format: TimestampFormat, timestamps: ndarray) -> ndarray:
        if result_timestamps is None:
            if timestamp_format != TimestampFormat.NONE:
                result_timestamps = timestamps
        else:
            if timestamp_format != TimestampFormat.NONE and not np.array_equal(result_timestamps, timestamps):
                raise RuntimeError(
                    "Cannot combine channels with different timestamps. "
                    "Try fetching data for each channel individually."
                )
        return result_timestamps

    def read_reduced(
        self, ch_name: Union[str, int],
        timestamp_format: TimestampFormat = TimestampFormat.SECONDS_SINCE_START,
        max_samples: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Read the reduced data from the given channel

        Returned DataFrame columns: timestamps, min, max, avg, rms
        """
        ch_id = self.__resolve_channel(ch_name)
        ch_config = self.__channels[ch_id]
        data: List[np.float64] = []
        timestamps: List[np.float64] = []

        if ch_config.reduced_sample_type == SampleType.INVALID:
            return pd.DataFrame()

        if ch_config.reduced_sample_type == SampleType.REDUCED:
            old_max_sweep_samples: int = 0

            for sweep in ch_config.reduced_sweeps:
                max_sweep_samples = sweep.max_samples
                if max_samples is not None:
                    max_sweep_samples = min(max_sweep_samples, max_samples)

                if old_max_sweep_samples != max_sweep_samples:
                    reduced_samples = (DmdSampleValueReduced * max_sweep_samples)()
                    reduced_timestamps = (c_double * max_sweep_samples)()
                    old_max_sweep_samples = max_sweep_samples

                (
                    num_valid_samples,
                    next_reduced_sample
                ) = _api.get_samples_and_ts_reduced_value_seconds(
                    ch_config.handle,
                    sweep.first_sample,
                    max_sweep_samples,
                    reduced_samples,
                    reduced_timestamps
                )
                timestamps.append(np.frombuffer(reduced_timestamps, count=num_valid_samples).copy())
                data.append(np.frombuffer(reduced_samples, count=4*num_valid_samples).copy())
                if max_samples is not None:
                    max_samples -= num_valid_samples
                    if max_samples <= 0:
                        break

            if timestamps:
                timestamps = np.concatenate(timestamps)

            if data:
                data = np.concatenate(data)

            if timestamp_format == TimestampFormat.NONE:
                data_frame = pd.DataFrame(dtype="float64")
            else:
                data_frame = pd.DataFrame(index=timestamps, dtype="float64")
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_MIN] = data[0::4]
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_MAX] = data[1::4]
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_AVG] = data[2::4]
            data_frame[DataFrameColumn.DATA_FRAME_COLUMN_REDUCED_RMS] = data[3::4]

            if timestamp_format in [
                TimestampFormat.ABSOLUTE_LOCAL_TIME,
                TimestampFormat.ABSOLUTE_UTC_TIME,
            ]:
                data_frame = self.__get_data_abs_timestamp_pandas(
                    data_frame, timestamp_format == TimestampFormat.ABSOLUTE_UTC_TIME
                )
            return data_frame

        raise NotImplementedError(
            f"Sampletype {ch_config.reduced_sample_type} not supported for reduced data"
        )

    def __gather_usable_channels(self, ch_names: Union[List[str], str, List[int], int]) -> List[int]:
        if isinstance(ch_names, (str, int)):
            # Convert single channel to list
            ch_names = [ch_names]

        used_channels = []
        sample_rate = None
        for ch_name in ch_names:
            ch_id = self.__resolve_channel(ch_name)
            ch_config = self.__channels[ch_id]

            if ch_config.raw_sample_type != SampleType.INVALID:
                used_channels.append(ch_id)

            if sample_rate is None:
                sample_rate = ch_config.sample_rate
            else:
                if sample_rate != ch_config.sample_rate:
                    raise RuntimeError("All requested channels need to have the same sample rate")

        return used_channels

    def __get_channel_infos(self) -> Dict[int, ChannelConfig]:
        """Read all channel infos"""
        channels = {}
        channel_type = ChannelType.ALL_CHANNELS
        for ch_idx in range(0, _api.get_num_channels(self.__file_handle, ChannelType.ALL_CHANNELS)):
            channel_handle, _ = _api.get_channels(self.__file_handle, channel_type, ch_idx, 1)
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

            channels[channel_handle.value] = ch_config
        return channels

    def __resolve_channel(self, channel_id: Union[str, int]) -> int:
        """
        Check if channel with a unique id (int) is available and return the id.
        Alternatively, the channel name can be used in this query to resolve the id.
        An exception is thrown if the channel name in not unique.

        @param channel_id: channel name or unique id
        @raise KeyError: If the channel is not found, a KeyError is raised.
        @return: unique id handle of the channel
        """
        if isinstance(channel_id, int):
            if channel_id not in self.__channels:
                raise KeyError(f"No channel with id ({channel_id}) can be found")
            return channel_id

        if isinstance(channel_id, str):
            resolved = None
            for key, channel in self.__channels.items():
                if channel.name == channel_id:
                    if resolved:
                        raise  KeyError(f"Channel with name ({channel_id}) is not unique")
                    resolved = key
            if resolved is None:
                raise  KeyError(f"No channel with given name ({channel_id}) can be found")
            return resolved

        raise TypeError("Channel should be referenced with string-name or int-ids")

    def __init_sample_and_timestamp_arrays(self, ch_config: ChannelConfig, block_size: int):
        max_sample_dimension = ch_config.max_sample_dimension

        if ch_config.raw_sample_type == SampleType.DOUBLE:
            sample_values = (c_double * block_size)()
            timestamp_values = (c_double * block_size)()
        elif ch_config.raw_sample_type == SampleType.SINT32:
            sample_values = (c_int32 * block_size)()
            timestamp_values = (c_double * block_size)()
        elif ch_config.raw_sample_type == SampleType.DOUBLE_VECTOR:
            sample_values = (c_double * (block_size * max_sample_dimension))()
            timestamp_values = (c_double * block_size)()
        elif ch_config.raw_sample_type == SampleType.COMPLEX_VECTOR:
            sample_values = (DmdSampleValueComplex * (block_size * max_sample_dimension))()
            timestamp_values = (c_double * block_size)()
        else:
            raise NotImplementedError(f"Sampletype {ch_config.raw_sample_type} not supported")

        return sample_values, timestamp_values


    def __get_all_sweeps(self, ch_config: ChannelConfig, max_samples:int = None) -> Tuple[np.ndarray, np.ndarray]:
        """Get data from all sweeps of given ch_config"""
        data: List[np.float64 | np.int32 | np.complex128] = []
        timestamps: List[np.float64] = []
        block_size = 1000000

        for sweep in ch_config.sweeps:
            first_sample = sweep.first_sample

            if max_samples == 0:
                break

            # HINT: Splitting up blocks is needed for async channels to reduce memory allocation
            old_max_sweep_samples: int = 0
            while first_sample <= sweep.last_sample:
                if sweep.last_sample - first_sample + 1 >= block_size:
                    max_sweep_samples = block_size
                else:
                    max_sweep_samples = sweep.last_sample - first_sample + 1

                if max_samples is not None:
                    max_sweep_samples = min(max_sweep_samples, max_samples)

                if old_max_sweep_samples != max_sweep_samples:
                    sample_values, timestamp_values = self.__init_sample_and_timestamp_arrays(ch_config,
                                                                                              max_sweep_samples)

                raw_timestamps, raw_values, next_sample = self.__get_single_sweep(ch_config,
                                                                                  first_sample,
                                                                                  max_sweep_samples,
                                                                                  sample_values,
                                                                                  timestamp_values)
                data.append(raw_values.copy())
                timestamps.append(raw_timestamps.copy())

                first_sample = next_sample
                old_max_sweep_samples = max_sweep_samples

                if max_samples is not None:
                    # subtract used-up samples
                    max_samples -= len(raw_timestamps)
                    if max_samples <= 0:
                        break

        if timestamps:
            timestamps = np.concatenate(timestamps)

        if data:
            data = np.concatenate(data)

        return timestamps, data


    def __get_ranged_sweeps(
        self, ch_config: ChannelConfig,
        start_time: float, end_time: float,
        max_samples: int = None
    ) -> Tuple[np.array, np.array]:
        actual_end_time = end_time if end_time is not None else ch_config.sweeps[-1].end_time

        timestamps: List[np.float64] = []
        data: List[np.float64 | np.int32 | np.complex128] = []

        # Get data from suitable sweeps
        old_max_sweep_samples: int = 0
        for sweep in ch_config.sweeps:
            if max_samples == 0:
                break
            if sweep.start_time <= actual_end_time and sweep.end_time >= start_time:
                if sweep.sample_frequency != 0:
                    # Sync channel
                    start_sample = int(start_time * sweep.sample_frequency)
                    end_sample = int(actual_end_time * sweep.sample_frequency)
                    first_sample, max_sweep_samples = self.__get_corrected_sample_count(sweep, start_sample, end_sample)

                    if max_samples is not None:
                        max_sweep_samples = min(max_sweep_samples, max_samples)

                    if old_max_sweep_samples != max_sweep_samples:
                        sample_values, timestamp_values = self.__init_sample_and_timestamp_arrays(ch_config,
                                                                                                  max_sweep_samples)
                        old_max_sweep_samples = max_sweep_samples

                    sweep_timestamps, sweep_data, *_ = self.__get_single_sweep(ch_config,
                                                                               first_sample,
                                                                               max_sweep_samples,
                                                                               sample_values,
                                                                               timestamp_values)
                    timestamps.append(sweep_timestamps.copy())
                    data.append(sweep_data.copy())

                    if max_samples is not None:
                        max_samples -= len(sweep_timestamps)
                else:
                    # Async channel (synthesize underlying sample_frequency from sweep parameters)
                    sample_frequency = (sweep.max_samples - 1) / (sweep.end_time - sweep.start_time)
                    start_sample = int(start_time * sample_frequency)
                    end_sample = int(actual_end_time * sample_frequency)
                    first_sample, max_sweep_samples = self.__get_corrected_sample_count(sweep, start_sample, end_sample)
                    last_sample = first_sample + max_sweep_samples

                    block_size = ASYNC_BLOCK_SIZE
                    while first_sample <= last_sample:
                        if last_sample - first_sample + 1 >= block_size:
                            block_max_samples = block_size
                        else:
                            block_max_samples = last_sample - first_sample + 1

                        if max_samples is not None:
                            block_max_samples = min(block_max_samples, max_samples)

                        if old_max_sweep_samples != max_sweep_samples:
                            sample_values, timestamp_values = self.__init_sample_and_timestamp_arrays(ch_config,
                                                                                                      block_max_samples)
                            old_max_sweep_samples = max_sweep_samples

                        raw_timestamps, raw_values, next_sample = self.__get_single_sweep(
                            ch_config, first_sample, block_max_samples, sample_values, timestamp_values
                        )

                        if len(raw_timestamps) > 0:
                            num_samples = 0
                            if raw_timestamps[-1] <= actual_end_time:
                                timestamps.append(raw_timestamps.copy())
                                data.append(raw_values.copy())
                                num_samples = len(raw_timestamps)
                            else:
                                # Do not use sample values outside the requested range
                                last_valid = np.argmax(raw_timestamps > actual_end_time)
                                timestamps.append(raw_timestamps[:last_valid].copy())
                                data.append(raw_values[:(last_valid * ch_config.max_sample_dimension)].copy())
                                num_samples = last_valid

                            if max_samples is not None:
                                max_samples -= num_samples
                                if max_samples <= 0:
                                    break

                        first_sample = next_sample

        if timestamps:
            timestamps = np.concatenate(timestamps)

        if data:
            data = np.concatenate(data)

        return timestamps, data

    def __get_ranged_sweeps_by_index(
            self, ch_config: "ChannelConfig", start_sample: int, end_sample: int
    ) -> Tuple[np.array, np.array]:

        start_sample = int(start_sample)
        end_sample = int(end_sample)
        cumulative_max_samples = self.__get_cumulative_max_samples(ch_config)
        end_sample = self.__get_correct_end_sample(cumulative_max_samples, end_sample, ch_config)
        samples_to_read = end_sample - start_sample
        timestamps = np.array([], dtype="float64")
        data = np.array([])

        # Get data from suitable sweeps
        read_samples = 0
        for index, sweep in enumerate(ch_config.sweeps):
            sweep_start_sample_offset = start_sample - (cumulative_max_samples[index] - sweep.max_samples)
            first_sample = sweep_start_sample_offset + sweep.first_sample

            if sweep.first_sample <= first_sample <= sweep.last_sample and start_sample < end_sample:
                if sweep.sample_frequency != 0:
                    # Sync channel
                    last_sample = end_sample - start_sample + first_sample
                    samples_to_read = last_sample - first_sample

                    if last_sample > sweep.last_sample + 1:
                        samples_to_read = sweep.last_sample + 1 - first_sample

                    sweep_timestamps, sweep_data, *_ = self.__get_single_sweep(ch_config, first_sample,
                                                                               samples_to_read)
                    read_samples += len(sweep_data)
                    timestamps = np.r_[timestamps, sweep_timestamps]
                    data = np.r_[data, sweep_data]
                    start_sample += read_samples
                else:
                    # Async channel - read always from the beginning and slice
                    block_size = ASYNC_BLOCK_SIZE
                    block_max_samples = block_size if block_size <= samples_to_read else samples_to_read
                    left_samples = samples_to_read - read_samples
                    first_sample = sweep.first_sample
                    current_last_sample = 0
                    while first_sample <= sweep.last_sample and left_samples > 0:
                        sweep_timestamps, sweep_data, next_sample = self.__get_single_sweep(
                            ch_config, first_sample, block_max_samples
                        )

                        returned_samples = len(sweep_data)
                        current_last_sample += returned_samples
                        offset = current_last_sample - start_sample
                        if offset > 0:
                            length = len(sweep_data)
                            if length <= left_samples:
                                timestamps = np.r_[timestamps, sweep_timestamps]
                                data = np.r_[data, sweep_data]
                            else:
                                timestamps = np.r_[timestamps, sweep_timestamps[:left_samples]]
                                data = np.r_[data, sweep_data[:left_samples]]

                        first_sample = next_sample
                        read_samples = len(data)
                        left_samples = samples_to_read - read_samples

                    if first_sample >= sweep.last_sample:
                        start_sample = cumulative_max_samples[index] + 1

        return timestamps, data

    @staticmethod
    def __get_correct_end_sample(cumulative_max_samples: List[int], end_sample: Optional[int], ch_config: "ChannelConfig"):
        if end_sample is not None:
            end_sample = int(end_sample) if end_sample is not None else ch_config.sweeps[-1].last_sample
        if cumulative_max_samples:
            last_sample = cumulative_max_samples[-1]

            if end_sample > last_sample:
                end_sample = last_sample

        return end_sample

    @staticmethod
    def __get_cumulative_max_samples(ch_config: "ChannelConfig") -> List[int]:
        cumulative_max_samples = []
        cumulative = 0

        for sweep in ch_config.sweeps:
            cumulative += sweep.max_samples
            cumulative_max_samples.append(cumulative)
        return cumulative_max_samples

    @staticmethod
    def __get_single_sweep(
        ch_config: ChannelConfig, first_sample: int, max_samples: int,
        sample_values: "Array", timestamp_values: "Array"
    ) -> Tuple[np.ndarray, np.ndarray, int]:
        """Get data for given sweep of given channel"""
        timestamps_dtype = "float64"
        if ch_config.raw_sample_type == SampleType.DOUBLE:
            num_valid_samples, next_sample = _api.get_samples_and_ts_scaled_value_seconds(
                ch_config.handle,
                first_sample,
                max_samples,
                sample_values,
                timestamp_values
            )
        elif ch_config.raw_sample_type == SampleType.SINT32:
            # Digital
            num_valid_samples, next_sample = _api.get_samples_and_ts_digital_value_seconds(
                ch_config.handle,
                first_sample,
                max_samples,
                sample_values,
                timestamp_values
            )
        elif ch_config.raw_sample_type == SampleType.DOUBLE_VECTOR:
            num_valid_samples, next_sample = _api.get_samples_and_ts_scalar_vector_seconds(
                ch_config.handle,
                first_sample,
                max_samples,
                ch_config.max_sample_dimension,
                sample_values,
                timestamp_values
            )
        elif ch_config.raw_sample_type == SampleType.COMPLEX_VECTOR:
            num_valid_samples, next_sample = _api.get_samples_and_ts_complex_vector_seconds(
                ch_config.handle,
                first_sample,
                max_samples,
                ch_config.max_sample_dimension,
                sample_values,
                timestamp_values
            )
        else:
            raise NotImplementedError(f"Sampletype {ch_config.raw_sample_type} not supported")

        timestamps = np.frombuffer(timestamp_values, dtype=timestamps_dtype, count=num_valid_samples)
        data = np.frombuffer(sample_values, dtype=ch_config.dtype, count=num_valid_samples*ch_config.max_sample_dimension)

        return timestamps, data, next_sample

    @staticmethod
    def __get_corrected_sample_count(
        sweep: "Sweep", start_sample: int, end_sample: Optional[float] = None
    ) -> Tuple[int, int]:
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
    def __check_sweep_number(ch_config: ChannelConfig, sweep_no: int) -> None:
        """Check if given sweep number is valid for given ch_config"""
        if not 0 <= sweep_no < len(ch_config.sweeps):
            raise IndexError(
                f"Selected sweep number {sweep_no} not valid. Valid range: 0 .. {len(ch_config.sweeps) - 1}"
            )

    @staticmethod
    def __load_file(file_name: str) -> "c_void_p":
        """Open the dmd file"""
        return _api.open_file(file_name)

    def __get_data_abs_timestamp_pandas(self, data_frame, utc: bool = True) -> pd.DataFrame:
        """Convert Timestamp column to absolute timestamps"""
        start_time = self.measurement_start_time_utc if utc else self.measurement_start_time_local
        data_frame.index = start_time + pd.to_timedelta(data_frame.index, unit="s")
        return data_frame

    def __get_data_abs_timestamp_array(self, timestamps: np.ndarray, utc: bool = True) -> np.array:
        """Convert Timestamp column to absolute timestamps"""
        start_time = self.measurement_start_time_utc if utc else self.measurement_start_time_local
        start_time_np = (start_time + start_time.utcoffset()).to_datetime64()
        timestamps = start_time_np + np.timedelta64(1, "s") * timestamps
        return timestamps
