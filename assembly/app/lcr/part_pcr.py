'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
# pylint: disable=unused-argument
from assembly.graph_writer import GraphWriter


_REAGENTS = {'water': 23.0, 'mm_pcr': 25.0}

_BACKBONE_PRIMER = {4613: 'E2cprim',
                    4614: 'A1kprim',
                    6383: 'Oriprim',
                    6384: 'Oriprim'}


class PartPcrWriter(GraphWriter):
    '''Base class for generating Part PCR worklist graphs.'''

    def __init__(self, parts_ice, ice_helper, output_name='part_pcr'):
        self._parts_ice = parts_ice
        self._ice_helper = ice_helper
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        pass

    def _get_plasmid_primer(self, part_ice):
        return None, None


class GenericPartPcrWriter(PartPcrWriter):
    '''Class for generating Part PCR worklist graphs.'''

    def __init__(self, parts_ice, ice_helper, output_name='part_pcr'):
        PartPcrWriter.__init__(self, parts_ice, ice_helper, output_name)

    def _initialise(self):
        for part_id, part_ice in self._parts_ice.items():
            part_plasmid_ice, primer_id = self._get_plasmid_primer(part_ice)

            part_plasmid = self._add_vertex(part_plasmid_ice.get_ice_id(),
                                            {'is_reagent': False})
            mm = self._add_vertex(primer_id, {'is_reagent': True})
            part = self._add_vertex(part_id, {'is_reagent': False})

            self._add_edge(part_plasmid, part, {'Volume': 1.0})
            self._add_edge(mm, part, {'Volume': 49.0})

    def _get_plasmid_primer(self, part_ice):
        '''Get "parent" Plasmid from Part.'''
        part_metadata = part_ice.get_metadata()

        for parent in part_metadata['parents']:
            if parent['visible'] == 'OK':
                parent = self._ice_helper.get_ice_entry(parent['id'])
                linked_part_ids = \
                    [linked_part['id']
                     for linked_part in parent.get_metadata()['linkedParts']]

                if len(linked_part_ids) == 2 and \
                        part_metadata['id'] in linked_part_ids:
                    linked_part_ids.remove(part_metadata['id'])
                    return parent, _BACKBONE_PRIMER[linked_part_ids[0]]

        return None, None


class SpecificPartPcrWriter(PartPcrWriter):
    '''Class for generating Part PCR worklist graphs.'''

    def __init__(self, parts_ice, ice_helper, output_name='part_pcr',
                 phospho=True):
        self.__phospho = phospho
        PartPcrWriter.__init__(self, parts_ice, ice_helper, output_name)

    def _initialise(self):
        mm = self._add_vertex('mm', {'is_reagent': True})

        for part_id, part_ice in self._parts_ice.items():
            part_plasmid_ice, primer_id = self._get_plasmid_primer(part_ice)

            part_plasmid = self._add_vertex(part_plasmid_ice.get_ice_id(),
                                            {'is_reagent': False})
            primer = self._add_vertex(primer_id, {'is_reagent': False})
            part = self._add_vertex(part_id, {'is_reagent': False})

            self._add_edge(part_plasmid, part, {'Volume': 1.0})
            self._add_edge(primer, part, {'Volume': 1.0})
            self._add_edge(mm, part, {'Volume': 48.0})

    def _get_plasmid_primer(self, part_ice):
        '''Get "parent" Plasmid from Part.'''
        part_metadata = part_ice.get_metadata()

        for parent in part_metadata['parents']:
            if parent['visible'] == 'OK':
                parent = self._ice_helper.get_ice_entry(parent['id'])
                linked_parts = parent.get_metadata()['linkedParts']

                # Ideally, should have two linked_parts: the part and the
                # vector backbone.
                # Unfortunately some legacy entries are missing a backbone.
                if len(linked_parts) < 3:
                    for linked_part in linked_parts:
                        if linked_part['type'] == 'PART':
                            return parent, parent.get_ice_id() + \
                                '_P' if self.__phospho else '_NP'

        return None, None
