'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
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


class InnerBlockWriter(GraphWriter):
    '''Class for generating inner block worklist graphs.'''

    def __init__(self, designs, inner_vol, outer_vol, mm_vol, output_name):
        self.__designs = designs
        self._inner_vol = inner_vol
        self._outer_vol = outer_vol
        self.__mm_vol = mm_vol
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for design_idx, design in enumerate(self.__designs):
            for block_idx, block in enumerate(design):
                block_id = str(design_idx + 1) + '.' + str(block_idx + 1)

                pcr = self._add_vertex(block_id + '.b', {'is_reagent': False})

                mm = self._add_vertex('mm', {'is_reagent': True})
                self._add_edge(mm, pcr, {'Volume': self.__mm_vol})

                inner_pool_id = block_id + '.ib'
                inner_pool = self._add_vertex(inner_pool_id,
                                              {'is_reagent': False})

                self._add_edge(inner_pool, pcr,
                               {'Volume': self._inner_vol})

                # Add outer oligos:
                for oligo_id in [block[idx] for idx in [0, -1]]:
                    outer_oligo = self._add_vertex(oligo_id,
                                                   {'is_reagent': False})

                    self._add_edge(outer_oligo, pcr,
                                   {'Volume': self._outer_vol})
