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

print("Measurement start time (utc): {}".format(dmd_file.measurement_start_time_utc))
print("Local measurement start time: {}".format(dmd_file.measurement_start_time_local))
print("Duration of the measurement: {:.4} seconds".format(dmd_file.measurement_duration))

if dmd_file.version.supports(1,2):
    print("Config: " + dmd_file.configuration_xml)

print("Channels:")
channel_names = dmd_file.channel_names
print("All accessible channel names: {}".format(channel_names))

print("Marker:")
for marker in dmd_file.markers:
    print(marker)

print("Global header:")
for header in dmd_file.headers:
    print(header)

print()

print("Fetching data for channels {} in the time interval 0.1s and 0.2s".format(channel_names[0:2]))
data = dmd_file.read_dataframe(
    channel_names[0:2], timestamp_format=pyDmdReader.TimestampFormat.ABSOLUTE_LOCAL_TIME, start_time=0.1, end_time=0.2
)
print("Data as pandas DataFrame:")
print(data)

if plt is not None:
    # Only, if matplotlib is installed
    data.plot(kind="line")
    plt.show()

# Cleanup
dmd_file.close()
pyDmdReader.dispose()
