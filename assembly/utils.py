'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=wrong-import-order
import os

import pandas as pd


def rename_cols(dir_name):
    '''Rename columns to SYNBIOCHEM-specific headers.'''
    columns = {'src_name': 'ComponentName',
               'src_plate': 'SourcePlateBarcode',
               'src_well': 'SourcePlateWell',
               'dest_plate': 'DestinationPlateBarcode',
               'dest_well': 'DestinationPlateWell'}

    for(dirpath, _, filenames) in os.walk(dir_name):
        for filename in filenames:
            if filename == 'worklist.csv':
                filepath = os.path.join(dirpath, filename)
                df = pd.read_csv(filepath)
                df.rename(columns=columns, inplace=True)
                df.to_csv(filepath, encoding='utf-8', index=False)
