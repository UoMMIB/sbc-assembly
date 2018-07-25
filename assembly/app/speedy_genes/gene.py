'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from collections import defaultdict
import itertools

from assembly.app.speedy_genes import get_dil_oligo_id, get_block_id, \
    get_design_id, get_pos_muts
from assembly.app.speedy_genes.pcr import PcrWriter


# from functools import reduce
class GenePcrWriter(PcrWriter):
    '''Class for generating gene PCR worklist graphs.'''

    def __init__(self, designs, comps_vol, primer_vol, mm_vol, output_name):
        self.__designs = designs
        PcrWriter.__init__(self, comps_vol, primer_vol, mm_vol, output_name)

    def _initialise(self):
        for design in self.__designs:
            pcr_comps_ids = [get_block_id(block_idx, block) + '_b'
                             for block_idx, block in enumerate(design)]

            primer_ids = [get_dil_oligo_id(design[0][0])[0],
                          get_dil_oligo_id(design[-1][-1])[0]]

            self._add_pcr(get_design_id(design), pcr_comps_ids, primer_ids)


class CombiGenePcrWriter(PcrWriter):
    '''Class for generating combinatorial gene PCR worklist graphs.'''

    def __init__(self, designs, max_muts, comps_vol, wt_primer_vol,
                 mut_primer_vol, total_vol, primer_ids, output_name):
        self.__designs = designs
        self.__primer_ids = primer_ids
        self.__max_muts = max_muts
        PcrWriter.__init__(self, comps_vol, wt_primer_vol, mut_primer_vol,
                           total_vol, output_name)

    def _initialise(self):
        pos_muts = defaultdict(set)

        for design in self.__designs:
            for block_idx, block in enumerate(design):
                block_id = get_block_id(block_idx, block)
                pos, muts = get_pos_muts(block_id)
                pos_muts[pos].add(muts)

        combis = [list(muts) for pos, muts in pos_muts.items()]
        combis = [combi for combi in itertools.product(*combis)
                  if sum(combi) <= self.__max_muts]

        for combi in combis:
            pcr_comps_ids = []

            for pos, muts in enumerate(combi):
                pool_id = str(pos + 1) + '_' + \
                    (str(muts) if muts > 0 else 'wt') + '_p'

                pcr_comps_ids.append(pool_id)

            self._add_pcr('-'.join([pcr_comps_id[:-2]
                                    for pcr_comps_id in pcr_comps_ids]),
                          pcr_comps_ids, self.__primer_ids)
