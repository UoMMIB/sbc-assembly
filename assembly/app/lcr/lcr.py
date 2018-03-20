'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
import sys
from igraph import Graph
from synbiochem.utils.graph_utils import add_edge, add_vertex

from assembly.app.lcr import utils


class LcrWriter(object):
    '''Class for generating LCR worklist graphs.'''

    def __init__(self, plasmid_parts):
        self.__plasmid_parts = plasmid_parts

    def get_graph(self):
        '''Get graph.'''
        graph = Graph(directed=True)

        water = add_vertex(graph, 'water', {'is_reagent': True})
        ampligase = add_vertex(graph, 'ampligase', {'is_reagent': True})
        mm = add_vertex(graph, 'mm', {'is_reagent': True})

        domino_vol = 1.75
        mm_vol = 7.0
        ampligase_vol = 1.5
        domino_pool_vol = 1.0
        part_vol = 1.0

        for plasmid_id, parts_map in self.__plasmid_parts.iteritems():
            # Make domino pools:
            domino_pool_water_vol = 250
            plasmid_water_vol = 25

            domino_pool = add_vertex(graph, plasmid_id + '_dominoes',
                                     {'is_reagent': False})

            for ice_id, part_ice in parts_map.iteritems():
                if part_ice.get_parameter('Type') == 'DOMINO':
                    domino = add_vertex(graph, ice_id,
                                        {'is_reagent': False})

                    add_edge(graph, domino, domino_pool,
                             {'Volume': domino_vol})

                    domino_pool_water_vol -= domino_vol

            add_edge(graph, water, domino_pool,
                     {'Volume': domino_pool_water_vol})

            # Make lcr plate:
            plasmid = add_vertex(graph, plasmid_id, {'is_reagent': False})

            add_edge(graph, mm, plasmid, {'Volume': mm_vol})
            add_edge(graph, ampligase, plasmid, {'Volume': ampligase_vol})
            add_edge(graph, domino_pool, plasmid, {'Volume': domino_pool_vol})

            plasmid_water_vol -= (mm_vol + ampligase_vol + domino_pool_vol)

            for ice_id, part_ice in parts_map.iteritems():
                if part_ice.get_parameter('Type') != 'DOMINO':
                    part = add_vertex(graph, ice_id, {'is_reagent': False})
                    add_edge(graph, part, plasmid, {'Volume': part_vol})
                    plasmid_water_vol -= part_vol

            add_edge(graph, water, plasmid, {'Volume': plasmid_water_vol})

        return graph


def main(args):
    '''main method.'''
    ice_helper = utils.ICEHelper(args[0], args[1], args[2])
    plasmid_parts = ice_helper.get_plasmid_parts(args[3:])
    writer = LcrWriter(plasmid_parts)
    graph = writer.get_graph()

    from synbiochem.utils.graph_utils import plot_graph
    plot_graph(graph, layout_name='tree')


if __name__ == '__main__':
    main(sys.argv[1:])
