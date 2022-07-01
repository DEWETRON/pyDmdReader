"""
Copyright DEWETRON GmbH 2022

Example that opens a simple DMD file with duplicate channel IDs
"""

import os
# Make sure the local module is used (can be omitted if byDmdReader is installed using pip)
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pyDmdReader

filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests", "data", "duplicate_names.dmd"))

with pyDmdReader.DmdReader(filename) as dmd:
    print("Channels found in file: {}".format(dmd.channel_names))

    # Read first two channels
    data = dmd.read_dataframe(dmd.channel_ids[0:2])
    print(data)
