'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


class InnerBlockWriter(GraphWriter):
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
