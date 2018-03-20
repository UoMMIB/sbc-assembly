'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


class PartQcWriter(GraphWriter):
    '''Class for generating Part qc worklist graphs.'''

    def __init__(self, part_ids, output_name='part_qc'):
        self.__part_ids = part_ids
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        ladder = self._add_vertex('ladder',
                                  {'is_reagent': True, 'well': 'H12'})

        bffer = self._add_vertex('buffer', {'is_reagent': True})

        ladder_product = self._add_vertex('ladder_product',
                                          {'is_reagent': False, 'well': 'H12'})
        self._add_edge(ladder, ladder_product, {'Volume': 2.0})
        self._add_edge(bffer, ladder_product, {'Volume': 22.0})

        for part_id in self.__part_ids:
            part = self._add_vertex(part_id, {'is_reagent': False})
            product = self._add_vertex(part_id + '_product',
                                       {'is_reagent': False})

            self._add_edge(part, product, {'Volume': 1.0})
            self._add_edge(bffer, product, {'Volume': 23.0})
