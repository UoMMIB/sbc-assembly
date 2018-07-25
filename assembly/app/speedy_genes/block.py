'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.app.speedy_genes import get_dil_oligo_id, get_block_id, \
    get_pos_muts
from assembly.app.speedy_genes.pcr import PcrWriter
from assembly.graph_writer import GraphWriter


class InnerBlockPoolWriter(GraphWriter):
    '''Class for generating pooled inner block worklist graphs.'''

    def __init__(self, designs, oligo_vol, output_name):
        self.__designs = designs
        self.__oligo_vol = oligo_vol
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        block_ids = []

        for design in self.__designs:
            for block_idx, block in enumerate(design):
                block_id = get_block_id(block_idx, block)

                if block_id not in block_ids:
                    inner_pool_id = block_id + '_ib'

                    inner_pool = self._add_vertex(inner_pool_id,
                                                  {'is_reagent': False})

                    # Pool *inner* oligos:
                    for oligo_id in block[1:-1]:
                        oligo = self._add_vertex(get_dil_oligo_id(oligo_id)[0],
                                                 {'is_reagent': False})

                        self._add_edge(oligo, inner_pool,
                                       {'Volume': self.__oligo_vol})

                    block_ids.append(block_id)


class BlockPcrWriter(PcrWriter):
    '''Class for generating block PCR worklist graphs.'''

    def __init__(self, designs, comps_vol, wt_primer_vol, mut_primer_vol,
                 mm_vol, output_name):
        self.__designs = designs
        PcrWriter.__init__(self, comps_vol, wt_primer_vol, mut_primer_vol,
                           mm_vol, output_name)

    def _initialise(self):
        block_ids = []

        for design in self.__designs:
            for block_idx, block in enumerate(design):
                block_id = get_block_id(block_idx, block)

                if block_id not in block_ids:
                    pcr_comps_ids = [block_id + '_ib']
                    pcr_id = block_id + '_b'
                    primer_ids = [get_dil_oligo_id(block[idx])
                                  for idx in [0, -1]]

                    self._add_pcr(pcr_id, pcr_comps_ids, primer_ids)

                block_ids.append(block_id)


class BlockPoolWriter(GraphWriter):
    '''Class for generating pooled block worklist graphs.'''

    def __init__(self, designs, pool_vol, output_name):
        self.__designs = designs
        self.__pool_vol = pool_vol
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        pool_steps = {}

        for design in self.__designs:
            for block_idx, block in enumerate(design):
                block_id = get_block_id(block_idx, block)
                pcr_id = block_id + '_b'
                pool_id = '_'.join([str(val) if val > 0 else 'wt'
                                    for val in get_pos_muts(block_id)]) + '_p'

                pool_steps[pcr_id] = pool_id

        for pcr_id, pool_id in pool_steps.items():
            pcr = self._add_vertex(pcr_id, {'is_reagent': False})
            pool = self._add_vertex(pool_id, {'is_reagent': False})

            self._add_edge(pcr, pool, {'Volume': self.__pool_vol})
