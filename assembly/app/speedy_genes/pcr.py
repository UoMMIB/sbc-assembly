'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


class PcrWriter(GraphWriter):
    '''Class for generating PCR worklist graphs.'''

    def __init__(self, comps_vol, primer_vol, mm_vol, output_name):
        self._comps_vol = comps_vol
        self._primer_vol = primer_vol
        self.__mm_vol = mm_vol
        GraphWriter.__init__(self, output_name)

    def _add_pcr(self, pcr_id, pcr_comps_ids, primer_ids):
        '''Add PCR reaction to worklist graph.'''
        pcr = self._add_vertex(pcr_id, {'is_reagent': False})

        mm = self._add_vertex('mm', {'is_reagent': True})
        self._add_edge(mm, pcr, {'Volume': self.__mm_vol})

        for pcr_comps_id in pcr_comps_ids:
            pcr_comps = self._add_vertex(pcr_comps_id,
                                         {'is_reagent': False})

            self._add_edge(pcr_comps, pcr, {'Volume': self._comps_vol})

        # Add outer oligos:
        for primer_ids in primer_ids:
            primer = self._add_vertex(primer_ids,
                                      {'is_reagent': False})

            self._add_edge(primer, pcr,
                           {'Volume': self._primer_vol})
