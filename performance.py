import pyDmdReader
import cProfile
import pstats
from pstats import SortKey
import os.path

test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tests/data"))
#filename =  os.path.join(test_data_dir, 'simple.dmd')
#filename = os.path.join(test_data_dir, 'hsrecording.dmd')
filename = "C:\\DATA\\TEDOMSCHNELL_Flexi230_2019_05_02_163147_009.dmd"

dmd_file = pyDmdReader.DmdReader(filename)
#channel = dmd_file.channel_names[0]
channel = 'U1_hRMS@POWER/0'

def readDataFrame(channel, timestamp_format):
    data = dmd_file.get_data_dataframe(channel, timestamp_format=timestamp_format)
    return

def timePandas():
    import timeit
    num = 1
    setup = "from __main__ import readDataFrame, channel; import pyDmdReader"    
    print("No timestamp:       {:.3f}".format(timeit.timeit("readDataFrame(channel, pyDmdReader.TimestampFormat.NONE)", setup=setup, number=num)))
    print("Simple timestamp:   {:.3f}".format(timeit.timeit("readDataFrame(channel, pyDmdReader.TimestampFormat.SECONDS_SINCE_START)", setup=setup, number=num)))
    print("Absolute timestamp: {:.3f}".format(timeit.timeit("readDataFrame(channel, pyDmdReader.TimestampFormat.ABSOLUTE_LOCAL_TIME)", setup=setup, number=num)))

def tracePandas():
    cProfile.run("readDataFrame(channel, pyDmdReader.TimestampFormat.NONE)", 'trace.log')
    p = pstats.Stats('trace.log')
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats()

if __name__ == '__main__':
    timePandas()
    tracePandas()
