'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


class OligoDilutionWriter(GraphWriter):
    '''Class for generating oligo dilution worklist graphs.'''

    def __init__(self, oligo_ids, oligo_vol, water_vol, output_name):
        self.__oligo_ids = oligo_ids
        self.__oligo_vol = oligo_vol
        self.__water_vol = water_vol
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for oligo_id in self.__oligo_ids:
            oligo = self._add_vertex(oligo_id, {'is_reagent': False})
            water = self._add_vertex('water', {'is_reagent': True})
            oligo_dil = self._add_vertex(oligo_id + '_dil',
                                         {'is_reagent': False})
            self._add_edge(oligo, oligo_dil, {'Volume': self.__oligo_vol})
            self._add_edge(water, oligo_dil, {'Volume': self.__water_vol})
