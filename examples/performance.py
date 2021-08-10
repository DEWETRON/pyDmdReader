import pyDmdReader
import cProfile
import pstats
from pstats import SortKey
import os.path

test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tests/data"))
filename =  os.path.join(test_data_dir, 'simple.dmd')
#filename = os.path.join(test_data_dir, 'hsrecording.dmd')

dmd_file = pyDmdReader.DmdReader(filename)

def readDataFrame(timestamp_format):
    dmd_file.get_data_dataframe(dmd_file.channel_names[0], timestamp_format=timestamp_format)

def timePandas():
    import timeit
    num = 100
    setup = "from __main__ import readDataFrame\nimport pyDmdReader"    
    print("No timestamp:       {:.3f}".format(timeit.timeit("readDataFrame(pyDmdReader.TimestampFormat.NONE)", setup=setup, number=num)))
    print("Simple timestamp:   {:.3f}".format(timeit.timeit("readDataFrame(pyDmdReader.TimestampFormat.SECONDS_SINCE_START)", setup=setup, number=num)))
    print("Absolute timestamp: {:.3f}".format(timeit.timeit("readDataFrame(pyDmdReader.TimestampFormat.ABSOLUTE_LOCAL_TIME)", setup=setup, number=num)))

if __name__ == '__main__':
    timePandas()

    cProfile.run("readDataFrame(pyDmdReader.TimestampFormat.NONE)", 'trace.log')
    p = pstats.Stats('trace.log')
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats()

