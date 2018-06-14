'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


class WtOligoPoolWriter(GraphWriter):
    '''Class for generating oligo dilution worklist graphs.'''

    def __init__(self, wt_mut, oligo_vol, output_name):
        self.__wt_mut = wt_mut
        self.__oligo_vol = oligo_vol
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for wt_id, mut_ids in self.__wt_mut.items():
            pool = self._add_vertex(str(wt_id) + 'm', {'is_reagent': False})

            for mut_id in mut_ids:
                oligo = self._add_vertex(mut_id, {'is_reagent': False})
                self._add_edge(oligo, pool, {'Volume': 10.0})
