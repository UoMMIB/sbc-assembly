'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
from collections import defaultdict
import sys

from Bio.Seq import Seq
from synbiochem.utils import dna_utils, seq_utils

from assembly.app.lcr import utils


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
        rev_comp = Seq(digest).reverse_complement()
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
    restr_enz = args[3].split(',')
    tm = float(args[4])
    mg_conc = float(args[5])
    primers = get_primers(ice_details, args[6:], restr_enz, tm, mg_conc)

    for part_id in sorted(primers):
        print '\t'.join(map(str, [part_id] + [val for pair in primers[part_id]
                                              for val in pair]))


if __name__ == '__main__':
    main(sys.argv[1:])
