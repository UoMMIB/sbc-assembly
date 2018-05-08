'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
from collections import defaultdict
import sys

from Bio.Seq import Seq
from synbiochem.utils import dna_utils, seq_utils

from assembly import plate
from assembly.app.lcr import utils
import pandas as pd


def get_primers(ice_details, part_ids, restr_enz, tm, mg_conc):
    '''Get primers for Parts by id.'''
    primers = defaultdict(list)

    ice_helper = utils.ICEHelper(ice_details['url'],
                                 ice_details['username'],
                                 ice_details['password'])

    reag_conc = {seq_utils.MG: mg_conc}

    for part_id in sorted(part_ids):
        entry = ice_helper.get_ice_entry(part_id)
        digest = _apply_restricts(entry.get_dna(), restr_enz)['seq']
        rev_comp = str(Seq(digest).reverse_complement())
        primers[part_id] = \
            [seq_utils.get_seq_by_melt_temp(digest, tm,
                                            reagent_concs=reag_conc),
             seq_utils.get_seq_by_melt_temp(rev_comp, tm,
                                            reagent_concs=reag_conc)]

    return primers


def _apply_restricts(dna, restr_enz):
    '''Apply restruction enzyme.'''
    if not restr_enz:
        return dna

    restrict_dnas = dna_utils.apply_restricts(dna, restr_enz)

    # This is a bit fudgy...
    # Essentially, return the longest fragment remaining after digestion.
    # Assumes prefix and suffix are short sequences that are cleaved off.
    restrict_dnas.sort(key=lambda x: len(x['seq']), reverse=True)
    return restrict_dnas[0]


def main(args):
    '''main method.'''
    ice_details = dict(zip(['url', 'username', 'password'], args[:3]))

    plates = [plate.from_table(filename) for filename in args[6:]]
    part_ids = [part_id
                for sublist in [plt.get_all() for plt in plates]
                for part_id in sublist]

    primers = get_primers(ice_details, part_ids, args[3].split(','),
                          float(args[4]), float(args[5]))
    plt = plate.Plate(name='plt')

    primer_plates = defaultdict(list)

    for part_id, primer_pair in primers.iteritems():
        part_locs = plate.find(plates, part_id)
        plate_id = part_locs.keys()[0]
        row_col = part_locs.values()[0][0]
        row, col = plate.get_indices(row_col)

        nonphospho = primer_plates[plate_id + '_primer_nonphospho']
        phospho = primer_plates[plate_id + '_primer_phospho']
        nonphospho.append(
            [row_col, part_id + '_F', primer_pair[0][0], row, col])
        nonphospho.append(
            [row_col, part_id + '_R', primer_pair[1][0], row, col])
        phospho.append(
            [row_col, part_id + '_F', '/5Phos/' + primer_pair[0][0], row, col])
        phospho.append(
            [row_col, part_id + '_R', '/5Phos/' + primer_pair[1][0], row, col])

    columns = ['Well Position', 'Sequence Name', 'Sequence', 'row', 'column']

    for plate_id, plt in primer_plates.iteritems():
        df = pd.DataFrame(plt, columns=columns)
        df.sort_values(['row', 'column'], inplace=True)
        df.drop(['row', 'column'], axis=1, inplace=True)
        df.to_csv(plate_id + '.csv', index=False, encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1:])
