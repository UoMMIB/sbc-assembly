'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.graph_writer import GraphWriter


_REAGENTS = {'water': 23.0, 'mm_pcr': 25.0}

_BACKBONE_PRIMER = {4613: 'E2cprim',
                    4614: 'A1kprim',
                    6383: 'Oriprim',
                    6384: 'Oriprim'}


class PartPcrWriter(GraphWriter):
    '''Class for generating Part PCR worklist graphs.'''

    def __init__(self, parts_ice, ice_helper, output_name='part_pcr'):
        self.__parts_ice = parts_ice
        self.__ice_helper = ice_helper
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        for part_id, part_ice in self.__parts_ice.iteritems():
            part_plasmid_ice, primer_id = self.__get_plasmid_primer(part_ice)

            part_plasmid = self._add_vertex(part_plasmid_ice.get_ice_id(),
                                            {'is_reagent': False})
            mm = self._add_vertex(primer_id, {'is_reagent': True})
            part = self._add_vertex(part_id, {'is_reagent': False})

            self._add_edge(part_plasmid, part, {'Volume': 1.0})
            self._add_edge(mm, part, {'Volume': 49.0})

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
