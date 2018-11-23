'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
from assembly.graph_writer import GraphWriter


class ColonyPcrWriter(GraphWriter):
    '''Class for generating colony PCR worklist graphs.'''

    def __init__(self, colony_ids, output_name='colony_pcr'):
        self.__colony_ids = colony_ids
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for colony_id in self.__colony_ids:

            colony_pcr = self._add_vertex(colony_id + '_pcr',
                                          {'is_reagent': False})

            mm = self._add_vertex('mm', {'is_reagent': True})
            colony = self._add_vertex(colony_id, {'is_reagent': False})

            self._add_edge(mm, colony_pcr, {'Volume': 5.0})
            self._add_edge(colony, colony_pcr, {'Volume': 2.5})
