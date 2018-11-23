'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
import os
import sys
from time import gmtime, strftime

from assembly import pipeline, plate, worklist
from assembly.app.plasmid_analysis import colony_pcr
import pandas as pd


def _get_colony_plates(filename):
    '''Get colony plates.'''
    colony_df = pd.read_csv(filename)
    plates = {}
    all_colony_ids = []

    for idx, plate_df in colony_df.groupby('DWPBarcode'):
        plate_df = plate_df[['DWPWell', 'ColonyID']]
        plate_df.columns = ['well', 'id']
        plates[idx] = plate.from_table(plate_df, idx)
        all_colony_ids.append(plate_df.values.tolist())

    return plates, all_colony_ids


def _get_frag_anal_labels(input_plates, out_dir_name):
    '''Get fragment analysis plates.'''
    for name, plt in input_plates.items():
        components = plt.get_all()
        labels = [[plate.get_idx(*plate.get_indices(pos), col_ord=True) + 1,
                   pos, vals['id']]
                  for pos, vals in components.items()]

        df = pd.DataFrame(labels)
        df.to_csv(os.path.join(out_dir_name, name + '_frag_anal.csv'),
                  index=False, header=False)


def main(args):
    '''main method.'''
    dte = strftime("%y%m%d", gmtime())
    out_dir_name = os.path.join(args[4], dte + args[2])

    # Parse colony pick output:
    colony_plates, colony_ids = _get_colony_plates(args[0])

    input_plates = pipeline.get_input_plates(args[1])
    input_plates.update(colony_plates)

    #  Write PCR worklists:
    writers = [colony_pcr.ColonyPcrWriter(colony_ids, dte + 'PCR' + args[2])]
    pipeline.run(writers, input_plates, {'reagents': args[3]}, out_dir_name)
    worklist.format_worklist(out_dir_name)

    # Generate fragment analyse labels:
    _get_frag_anal_labels(colony_plates, out_dir_name)


if __name__ == '__main__':
    main(sys.argv[1:])
