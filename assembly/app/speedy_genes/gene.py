'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.app.speedy_genes import get_dil_oligo_id, get_block_id, \
    get_design_id
from assembly.app.speedy_genes.pcr import PcrWriter


class GenePcrWriter(PcrWriter):
    '''Class for generating gene PCR worklist graphs.'''

    def __init__(self, designs, comps_vol, primer_vol, mm_vol, output_name):
        self.__designs = designs
        PcrWriter.__init__(self, comps_vol, primer_vol, mm_vol, output_name)

    def _initialise(self):
        for design in self.__designs:
            pcr_comps_ids = [get_block_id(block_idx, block) + '_b'
                             for block_idx, block in enumerate(design)]

            primer_ids = [get_dil_oligo_id(design[0][0]),
                          get_dil_oligo_id(design[-1][-1])]

            self._add_pcr(get_design_id(design), pcr_comps_ids, primer_ids)
