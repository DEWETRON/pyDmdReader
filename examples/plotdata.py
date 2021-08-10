"""
Example that opens a simple DMD file, shows the information about the recording and plots some data from the second channel
"""

import pyDmdReader
import matplotlib.pyplot as plt

dmd_file = pyDmdReader.DmdReader('tests/data/simple.dmd')

print("Local measurement start time (utc): {}".format(dmd_file.measurement_start_time_utc))
print("Measurement start time (local): {}".format(dmd_file.measurement_start_time_local))

print("Channels:")
channel_names = dmd_file.channel_names
print("All accessible channel names: {}".format(channel_names))

print("Marker:")
for marker in dmd_file.get_markers():
    print(marker)

print("Global header:")
for header in dmd_file.get_header():
    print(header)

print()

print("Fetching data for channels {}".format(channel_names[0:2]))
data = dmd_file.get_data_dataframe(channel_names[0:2], timestamp_format=pyDmdReader.TimestampFormat.ABSOLUTE_LOCAL_TIME)
print("Data as pandas DataFrame:")
print(data)

data[1:100].plot(kind='line')
plt.show()

# Cleanup
dmd_file.close()
pyDmdReader.dispose()
