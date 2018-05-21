'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=wrong-import-order
from collections import defaultdict
import sys

from Bio.Seq import Seq

from assembly import plate
from assembly.app.lcr import utils
import pandas as pd
from synbiochem.utils import dna_utils, seq_utils


class PrimerDesigner(object):
    '''Class to design primers.'''

    def __init__(self, ice_details):
        self.__ice_helper = utils.ICEHelper(ice_details['url'],
                                            ice_details['username'],
                                            ice_details['password'])

    def get_primers(self, plasmid_ids, plates, restr_enz, tm, mg_conc):
        '''Get primers for Parts by id.'''
        plasmid_parts = self.__ice_helper.get_plasmid_parts(plasmid_ids,
                                                            type_filter='PART')

        plasmid_primers = _get_primers(plasmid_parts, restr_enz, tm, mg_conc)

        return _get_plates(plasmid_primers, plates)


def _get_primers(plasmid_parts, restr_enz, tm, mg_conc):
    '''Design primers.'''
    plasmid_primers = defaultdict(list)
    reag_conc = {seq_utils.MG: mg_conc}

    for plasmid_id in plasmid_parts:
        parts = plasmid_parts[plasmid_id]
        digest = _apply_restricts(parts.values()[0].get_dna(),
                                  restr_enz)['seq']
        rev_comp = str(Seq(digest).reverse_complement())
        plasmid_primers[plasmid_id] = \
            [seq_utils.get_seq_by_melt_temp(digest, tm,
                                            reagent_concs=reag_conc),
             seq_utils.get_seq_by_melt_temp(rev_comp, tm,
                                            reagent_concs=reag_conc)]

    return plasmid_primers


def _get_plates(plasmid_primers, plates):
    '''Map primers to plates.'''
    primer_plates = defaultdict(list)

    for plasmid_id, primer_pair in plasmid_primers.iteritems():
        part_locs = plate.find(plates, plasmid_id)
        plate_id = part_locs.keys()[0]
        col_row = part_locs.values()[0][0]
        col, row = plate.get_indices(col_row)

        nonphospho = primer_plates[plate_id + '_primer_nonphospho']
        phospho = primer_plates[plate_id + '_primer_phospho']
        nonphospho.append(
            [col_row, plasmid_id + '_F', primer_pair[0][0], row, col])
        nonphospho.append(
            [col_row, plasmid_id + '_R', primer_pair[1][0], row, col])
        phospho.append(
            [col_row, plasmid_id + '_F', '/5Phos/' + primer_pair[0][0],
             row, col])
        phospho.append(
            [col_row, plasmid_id + '_R', '/5Phos/' + primer_pair[1][0],
             row, col])

    columns = ['Well Position', 'Sequence Name',
               'Sequence', 'row', 'column']

    for plate_id in primer_plates:
        df = pd.DataFrame(primer_plates[plate_id], columns=columns)
        df.sort_values(['row', 'column'], inplace=True)
        df.drop(['row', 'column'], axis=1, inplace=True)
        primer_plates[plate_id] = df

    return primer_plates


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
    designer = PrimerDesigner(ice_details)

    plates = [plate.from_table(filename) for filename in args[6].split(',')]

    primer_plates = designer.get_primers(args[7:], plates,
                                         args[3].split(','),
                                         float(args[4]), float(args[5]))

    for plate_id, plt in primer_plates.iteritems():
        plt.to_csv(plate_id + '.csv', index=False, encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1:])
