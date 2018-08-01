'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from assembly.app.speedy_genes import get_primers
from assembly.graph_writer import GraphWriter


class WtOligoDilutionWriter(GraphWriter):
    '''Class for generating wild-type oligo dilution worklist graphs.'''

    def __init__(self, oligo_ids, designs, primer_vol, oligo_vol, total_vol,
                 output_name):
        self.__oligo_ids = oligo_ids
        self.__primers = get_primers(designs)
        self.__primer_vol = primer_vol
        self.__oligo_vol = oligo_vol
        self.__total_vol = total_vol
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for oligo_id in self.__oligo_ids:
            oligo = self._add_vertex(oligo_id, {'is_reagent': False})
            water = self._add_vertex('water', {'is_reagent': True})
            oligo_dil = self._add_vertex(oligo_id + '_dil',
                                         {'is_reagent': False})

            vol = self.__primer_vol \
                if oligo_id in self.__primers else self.__oligo_vol

            self._add_edge(oligo, oligo_dil, {'Volume': vol})
            self._add_edge(water, oligo_dil,
                           {'Volume': self.__total_vol - vol})
