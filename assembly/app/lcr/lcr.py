'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
import sys

from assembly.app.lcr import utils
from assembly.graph_writer import GraphWriter


class LcrWriter(GraphWriter):
    '''Class for generating LCR worklist graphs.'''

    def __init__(self, plasmid_parts, output_name='lcr'):
        self.__plasmid_parts = plasmid_parts
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        water = self._add_vertex('water', {'is_reagent': True})
        ampligase = self._add_vertex('ampligase', {'is_reagent': True})
        mm = self._add_vertex('mm_lcr', {'is_reagent': True})

        domino_vol = 1.75
        mm_vol = 7.0
        ampligase_vol = 1.5
        domino_pool_vol = 1.0
        part_vol = 1.0

        for plasmid_id, parts_map in self.__plasmid_parts.iteritems():
            # Make domino pools:
            dom_pool_water_vol = 250
            plasmid_water_vol = 25

            domino_pool = self._add_vertex(plasmid_id + '_dominoes',
                                           {'is_reagent': False})

            for ice_id, part_ice in parts_map.iteritems():
                if part_ice.get_parameter('Type') == 'DOMINO':
                    domino = self._add_vertex(ice_id, {'is_reagent': False})

                    self._add_edge(domino, domino_pool, {'Volume': domino_vol})

                    dom_pool_water_vol -= domino_vol

            self._add_edge(water, domino_pool, {'Volume': dom_pool_water_vol})

            # Make lcr plate:
            plasmid = self._add_vertex(plasmid_id, {'is_reagent': False})

            self._add_edge(mm, plasmid, {'Volume': mm_vol})
            self._add_edge(ampligase, plasmid, {'Volume': ampligase_vol})
            self._add_edge(domino_pool, plasmid,  {'Volume': domino_pool_vol})

            plasmid_water_vol -= (mm_vol + ampligase_vol + domino_pool_vol)

            for ice_id, part_ice in parts_map.iteritems():
                if part_ice.get_parameter('Type') != 'DOMINO':
                    part = self._add_vertex(ice_id, {'is_reagent': False})
                    self._add_edge(part, plasmid, {'Volume': part_vol})
                    plasmid_water_vol -= part_vol

            self._add_edge(water, plasmid, {'Volume': plasmid_water_vol})


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
