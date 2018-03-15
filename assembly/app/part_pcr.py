'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from igraph import Graph

from synbiochem.utils.graph_utils import add_edge, add_vertex


_REAGENTS = {'water': 23.0, 'mm': 25.0}

_BACKBONE_PRIMER = {4613: 'E2cprim',
                    4614: 'A1kprim',
                    6383: 'Oriprim',
                    6384: 'Oriprim'}


class PartPcrWriter(object):
    '''Class for generating Part PCR worklist graphs.'''

    def __init__(self, parts_ice, ice_helper):
        self.__parts_ice = parts_ice
        self.__ice_helper = ice_helper

    def get_graph(self):
        '''Get graph.'''
        graph = Graph(directed=True)

        for part_id, part_ice in self.__parts_ice.iteritems():
            part_plasmid_ice, primer_id = self.__get_plasmid_primer(part_ice)

            part_plasmid = add_vertex(graph,
                                      part_plasmid_ice.get_ice_id(),
                                      {'is_reagent': False})
            master_mix = add_vertex(graph, primer_id, {'is_reagent': True})
            part = add_vertex(graph, part_id, {'is_reagent': False})

            add_edge(graph, part_plasmid, part, {'Volume': 1.0})
            add_edge(graph, master_mix, part, {'Volume': 49.0})

        return graph

    def __get_plasmid_primer(self, part_ice):
        '''Get "parent" Plasmid from Part.'''
        part_metadata = part_ice.get_metadata()

        for parent in part_metadata['parents']:
            if parent['visible'] == 'OK':
                parent = self.__ice_helper.get_ice_entry(parent['id'])
                linked_part_ids = \
                    [linked_part['id']
                     for linked_part in parent.get_metadata()['linkedParts']]

                if len(linked_part_ids) == 2 and \
                        part_metadata['id'] in linked_part_ids:
                    linked_part_ids.remove(part_metadata['id'])
                    return parent, _BACKBONE_PRIMER[linked_part_ids[0]]

        return None, None
