# Change Log

All notable changes to this project will be documented in this file.

## [7.2.1] - 2024-08-29
- Release community fixes
- Synchronized pyDmdReader ersioning to Oxygen version
- Compatibility to Oxygen 7.2.1

## [0.7.0] - 2023-07-24
- Release community fixes
- Compatibility to Oxygen 6.6

## [0.6.0] - planned

### Added
- all read_* methods now accept an optional `max_samples` parameter that limits the number of returned samples
- Support for reading the configuration XML from DMD files with the `configuration_xml` DmdReader property

### Changed
- Updated Windows binaries for Oxygen 6.2 compatibility

## [0.5.0] - 2022-07-01

### Added
- Support to use DmdReader with the `with` statement
- Support for loading DMDs with duplicate channel names
- DmdReader `channel_ids` returns a list of all unique channel IDs
- DmdReader `allchannels` returns a dictionary of all channels with a unique ID as key

### Changed
- `read_dataframe`, `read_array` and `read_reduced`  optionally use the unique channel ID (`int`) instead of the channel name (`str`)

## [0.4.0] - 2022-04-06

### Changed
- Fixed pyproject.toml to be used with recent pip install versions
- Updated Windows binaries for Oxygen 6.1 compatibility (no change in the python library)

## [0.3.0] - 2021-12-13

### Changed
- Updated Windows binaries for Oxygen 6.0 compatibility (no change in the python library)

## [0.2.0] - 2021-10-04

### Changed
- Python code cleanup

## [0.1.0] - 2021-08-13

This is the first production ready release

### Added
- Read data using `read_dataframe` or `read_array` methods with customizable timestamp format and possible time-ranges
- Data can now be read from multiple channels at the same time

### Changed
- Improvements of the overall DmdReader public interface
- This release breaks existing uses of the DmdReader 0.0.1

## [0.0.1] - 2021-08-05

Initial pre-production release
