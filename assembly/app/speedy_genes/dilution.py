'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


class WtOligoDilutionWriter(GraphWriter):
    '''Class for generating wildtype oligo dilution worklist graphs.'''

    def __init__(self, wt_oligo_ids, output_name='wt_dil'):
        self.__wt_oligo_ids = wt_oligo_ids
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for wt_oligo_id in self.__wt_oligo_ids:
            wt_oligo = self._add_vertex(wt_oligo_id, {'is_reagent': False})
            water = self._add_vertex('water', {'is_reagent': True})
            wt_oligo_dil = self._add_vertex(wt_oligo_id + '_dil',
                                            {'is_reagent': False})
            self._add_edge(wt_oligo, wt_oligo_dil, {'Volume': 10.0})
            self._add_edge(water, wt_oligo_dil, {'Volume': 190.0})
