'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=wrong-import-order
import os
import sys
from time import gmtime, strftime

from assembly import pipeline, worklist
from assembly import plate
from assembly.app.plasmid_analysis import colony_pcr
import pandas as pd


def _get_colony_plates(filename):
    '''Get colony plates.'''
    colony_df = pd.read_csv(filename)
    plates = {}
    colony_ids = []

    for idx, plate_df in colony_df.groupby('DWPBarcode'):
        plate_df = plate_df[['DWPWell', 'ColonyID']]
        plate_df.columns = ['well', 'id']
        plates[idx] = plate.from_table(plate_df, idx)
        colony_ids.extend(plate_df['id'].values)

    return plates, colony_ids


def main(args):
    '''main method.'''
    input_plates, colony_ids = _get_colony_plates(args[0])

    dte = strftime("%y%m%d", gmtime())

    writers = [colony_pcr.ColonyPcrWriter(colony_ids, dte + 'PCR' + args[1])]

    out_dir_name = os.path.join(args[3], dte + args[1])

    pipeline.run(writers, input_plates, {'reagents': args[2]}, out_dir_name)

    worklist.format_worklist(out_dir_name)


if __name__ == '__main__':
    main(sys.argv[1:])
