'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from igraph import Graph

from synbiochem.utils.graph_utils import add_edge, add_vertex


class PartDigestWriter(object):
    '''Class for generating Part digest worklist graphs.'''

    def __init__(self, part_ids):
        self.__part_ids = part_ids

    def get_graph(self):
        '''Get graph.'''
        graph = Graph(directed=True)

        for part_id in self.__part_ids:
            part = add_vertex(graph, part_id, {'is_reagent': False})
            primer_mix = add_vertex(graph, 'mm', {'is_reagent': True})
            add_edge(graph, primer_mix, part, {'Volume': 150.0})

        return graph
