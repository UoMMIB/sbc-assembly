'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


class PartDigestWriter(GraphWriter):
    '''Class for generating Part digest worklist graphs.'''

    def __init__(self, part_ids, output_name='part_dig'):
        self.__part_ids = part_ids
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for part_id in self.__part_ids:
            part = self._add_vertex(part_id, {'is_reagent': False})
            primer_mix = self._add_vertex('mm_dig', {'is_reagent': True})
            self._add_edge(primer_mix, part, {'Volume': 75.0})
