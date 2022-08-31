"""
Copyright DEWETRON GmbH 2021

Example that opens a simple DMD file, shows the information about the recording and plots some data from the second
channel (if matplotlib and dependencies are installed)
"""


import os
# Make sure the local module is used (can be omitted if byDmdReader is installed using pip)
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pyDmdReader
try:
    # Check if matplot lib is installed
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests", "data", "simple.dmd"))
dmd_file = pyDmdReader.DmdReader(filename)

print(f"Measurement start time (utc): {dmd_file.measurement_start_time_utc}")
print(f"Local measurement start time: {dmd_file.measurement_start_time_local}")
print(f"Duration of the measurement: {dmd_file.measurement_duration:.4} seconds")

if dmd_file.version.supports(1,2):
    print("Config: " + dmd_file.configuration_xml)

print("Channels:")
channel_names = dmd_file.channel_names
print(f"All accessible channel names: {channel_names}")

print("Channel information of first channel:")
channel = dmd_file.channels[channel_names[0]]
print(f"  Name: {channel.name}")
print(f"  Unit: {channel.unit}")
print(f"  Samplerate: {channel.sample_rate} Hz")

print("Marker:")
for marker in dmd_file.markers:
    print(marker)

print("Global header:")
for header in dmd_file.headers:
    print(header)

print()

selected_channels = channel_names[0:2]

print("Get first 10 samples with timestamp >= 0.5 as array:")
data, _ = dmd_file.read_array(
    selected_channels, timestamp_format=pyDmdReader.TimestampFormat.NONE, start_time=0.5, max_samples=10
)
print(data)

print(f"Fetching data for channels {selected_channels} in the time interval 0.1s and 0.2s")
data = dmd_file.read_dataframe(
    selected_channels, timestamp_format=pyDmdReader.TimestampFormat.ABSOLUTE_LOCAL_TIME, start_time=0.1, end_time=0.2
)
print(data)

if plt is not None:
    # Only, if matplotlib is installed
    data.plot(kind="line")
    plt.xlabel("Time")
    units = [dmd_file.channels[ch].unit for ch in selected_channels]
    plt.ylabel(", ".join(units))
    plt.show()

# Cleanup
dmd_file.close()
pyDmdReader.dispose()
