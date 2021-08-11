"""
Example that opens a simple DMD file, shows the information about the recording and plots some data from the second channel
"""

# Make sure the local module is used (can be omitted if byDmdReader is installed using pip)
import sys
sys.path.insert(0, "../pyDmdReader")

import pyDmdReader
import matplotlib.pyplot as plt
import os.path

filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tests/data/simple.dmd"))
dmd_file = pyDmdReader.DmdReader(filename)

print("Local measurement start time (utc): {}".format(dmd_file.measurement_start_time_utc))
print("Measurement start time (local): {}".format(dmd_file.measurement_start_time_local))

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

print("Fetching data for channels {}".format(channel_names[0:2]))
data = dmd_file.read_dataframe(channel_names[0:2], timestamp_format=pyDmdReader.TimestampFormat.ABSOLUTE_LOCAL_TIME)
print("Data as pandas DataFrame:")
print(data)

data[1:100].plot(kind='line')
plt.show()

# Cleanup
dmd_file.close()
pyDmdReader.dispose()
