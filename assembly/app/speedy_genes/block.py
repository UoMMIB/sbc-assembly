'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.app.speedy_genes.pcr import PcrWriter
from assembly.graph_writer import GraphWriter


class InnerBlockPoolWriter(GraphWriter):
    '''Class for generating pooled inner block worklist graphs.'''

    def __init__(self, designs, oligo_vol, output_name):
        self.__designs = designs
        self.__oligo_vol = oligo_vol
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for design_idx, design in enumerate(self.__designs):
            for block_idx, block in enumerate(design):
                inner_pool_id = str(design_idx + 1) + '.' + \
                    str(block_idx + 1) + '.ib'

                inner_pool = self._add_vertex(inner_pool_id,
                                              {'is_reagent': False})

                # Pool *inner* oligos:
                for oligo_id in block[1:-1]:
                    oligo = self._add_vertex(oligo_id,
                                             {'is_reagent': False})

                    self._add_edge(oligo, inner_pool,
                                   {'Volume': self.__oligo_vol})


class BlockPcrWriter(PcrWriter):
    '''Class for generating block PCR worklist graphs.'''

    def __init__(self, designs, comps_vol, primer_vol, mm_vol, output_name):
        self.__designs = designs
        PcrWriter.__init__(self, comps_vol, primer_vol, mm_vol, output_name)

    def _initialise(self):
        for design_idx, design in enumerate(self.__designs):
            for block_idx, block in enumerate(design):
                base_id = str(design_idx + 1) + '.' + str(block_idx + 1)
                pcr_comps_ids = [base_id + '.ib']
                pcr_id = base_id + '.b'
                primer_ids = [block[idx] for idx in [0, -1]]

                self._add_pcr(pcr_id, pcr_comps_ids, primer_ids)
