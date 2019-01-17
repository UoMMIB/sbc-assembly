'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
from functools import partial
import os
import re
import sys
from time import gmtime, strftime

from assembly import pipeline, plate, worklist
from assembly.app.plasmid_analysis import colony_pcr
import pandas as pd


def _get_colony_plates(filenames, input_plates):
    '''Get colony plates.'''
    barcode_plates = _get_barcode_plates(input_plates)

    col_dfs = []

    for filename in filenames:
        col_dfs.append(pd.read_csv(filename))

    colony_df = pd.concat(col_dfs, axis=0, ignore_index=True)

    colony_df.drop_duplicates(subset=['DWPBarcode', 'DWPWell'],
                              keep='last', inplace=True)
    colony_df.rename(columns={'DWPWell': 'well'}, inplace=True)

    colony_df['id'] = \
        colony_df['ColonyID'].apply(lambda x: x.split('_')[0])

    colony_df['plate_idx'] = \
        colony_df['DWPBarcode'].apply(lambda x: int(x.split('_')[-1]))

    _get_barcodes_plates = partial(_get_barcodes, barcode_plates)
    colony_df = colony_df.apply(_get_barcodes_plates, axis=1)

    plates = {}
    all_colony_ids = []

    for idx, plate_df in colony_df.groupby('DWPBarcode'):
        plate_df = plate_df[['well', 'id']]
        plates[idx] = plate.from_table(plate_df, idx)
        all_colony_ids.append(plate_df.values.tolist())

    return plates, all_colony_ids, \
        colony_df.rename(columns={'id': 'actual_ice_id'})


def _get_barcode_plates(input_plates):
    '''Get barcode plates.'''
    barcode_plates = {}

    for plt_id, plt in input_plates.items():
        search = re.search(r'(?<=ONT)(\d+)', plt_id)

        if search:
            barcode_plates[int(search.group(1))] = plt

    return barcode_plates


def _get_barcodes(barcode_plates, row):
    '''Get barcodes from colony picker table.'''
    properties = barcode_plates[row['plate_idx']].get_by_well(row['well'])
    row['forward'] = properties['forward']
    row['reverse'] = properties['reverse']
    return row


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
    out_dir_name = os.path.join(args[3], dte + args[1])
    input_plates = pipeline.get_input_plates(args[0])

    # Parse colony pick output:
    colony_plates, colony_ids, colony_df = _get_colony_plates(args[4:],
                                                              input_plates)

    input_plates.update(colony_plates)

    #  Write PCR worklists:
    writers = [colony_pcr.ColonyPcrWriter(colony_ids, dte + 'COL' + args[1])]
    pipeline.run(writers, input_plates, {'reagents': args[2]}, out_dir_name)
    worklist.format_worklist(out_dir_name)

    # Generate fragment analyse labels:
    colony_df.to_csv(os.path.join(out_dir_name, 'barcodes.csv'), index=False)

    pd.DataFrame(colony_df['actual_ice_id'].unique()).to_csv(os.path.join(
        out_dir_name, 'ice_ids.txt'), index=False, header=False)

    _get_frag_anal_labels(colony_plates, out_dir_name)


if __name__ == '__main__':
    main(sys.argv[1:])
