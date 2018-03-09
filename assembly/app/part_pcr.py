'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=ungrouped-imports
import sys

from igraph import Graph
from synbiochem.utils.ice_utils import ICEClient

from assembly.worklist import WorklistGenerator
from synbiochem.utils.graph_utils import add_edge, add_vertex


_REAGENTS = {'water': 23.0, 'mm': 25.0}

_BACKBONE_PRIMER = {4613: 'E2cprim',
                    4614: 'A1kprim',
                    6383: 'Oriprim',
                    6384: 'Oriprim'}


class PartPcrWriter(object):
    '''Class for writing Part PCR worklists.'''

    def __init__(self, ice_url, ice_username, ice_password):
        self.__ice_client = ICEClient(ice_url, ice_username, ice_password)
        self.__ice_entries = {}

    def get_graph(self, plasmid_ids):
        '''Get graph.'''
        graph = Graph(directed=True)

        for plasmid_id in plasmid_ids:
            for part_ice in self.__get_parts(plasmid_id):
                if part_ice.get_parameter('Type') != 'DOMINO':
                    part_id = part_ice.get_ice_id()
                    part_plasmid_ice, primer_id = \
                        self.__get_plasmid_primer(part_ice)

                    part_plasmid = add_vertex(graph,
                                              part_plasmid_ice.get_ice_id() +
                                              '(' + part_id + ')',
                                              {'is_reagent': False})
                    master_mix = add_vertex(graph, primer_id,
                                            {'is_reagent': True})
                    part = add_vertex(graph, part_id,
                                      {'is_reagent': False})

                    add_edge(graph, part_plasmid, part, {'Volume': 1.0})
                    add_edge(graph, master_mix, part, {'Volume': 24.0})

        return graph

    def __get_parts(self, plasmid_id):
        '''Get parts.'''
        ice_entry = self.__get_ice_entry(plasmid_id)
        part_ids = [part['id']
                    for part in ice_entry.get_metadata()['linkedParts']]

        return [self.__get_ice_entry(part_id) for part_id in part_ids]

    def __get_plasmid_primer(self, part):
        '''Get "parent" Plasmid from Part.'''
        part_metadata = part.get_metadata()

        for parent in part_metadata['parents']:
            if parent['visible'] == 'OK':
                parent = self.__get_ice_entry(parent['id'])
                linked_part_ids = \
                    [linked_part['id']
                     for linked_part in parent.get_metadata()['linkedParts']]

                if len(linked_part_ids) == 2 and \
                        part_metadata['id'] in linked_part_ids:
                    linked_part_ids.remove(part_metadata['id'])
                    return parent, _BACKBONE_PRIMER[linked_part_ids[0]]

        return None, None

    def __get_master_mix_id(self, part_id):
        '''Get master mix id.'''
        return 'mm'

    def __get_ice_entry(self, ice_id):
        '''Get ICE entry.'''
        if ice_id not in self.__ice_entries:
            ice_entry = self.__ice_client.get_ice_entry(ice_id)
            self.__ice_entries[ice_id] = ice_entry

        return self.__ice_entries[ice_id]


def main(args):
    '''main method.'''
    writer = PartPcrWriter(args[0], args[1], args[2])
    graph = writer.get_graph(args[3:])

    worklist_gen = WorklistGenerator(graph)
    worklist, plates = worklist_gen.get_worklist()

    for plate_id in sorted(plates, reverse=True):
        print 'Plate: ' + str(plate_id)
        print plates[plate_id]
        print

    print worklist


if __name__ == '__main__':
    main(sys.argv[1:])
