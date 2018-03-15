'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from synbiochem.utils.ice_utils import ICEClient


class ICEHelper(object):
    '''Helper class for accessing ICE.'''

    def __init__(self, ice_url, ice_username, ice_password):
        self.__ice_client = ICEClient(ice_url, ice_username, ice_password)
        self.__ice_entries = {}

    def get_parts(self, plasmid_ids):
        '''Get parts from plasmid ids.'''
        parts = {}

        for plasmid_id in plasmid_ids:
            for part_ice in self.__get_parts(plasmid_id):
                part_id = part_ice.get_ice_id()

                if part_id not in parts:
                    parts[part_id] = part_ice

        return parts

    def get_ice_entry(self, ice_id):
        '''Get ICE entry.'''
        if ice_id not in self.__ice_entries:
            ice_entry = self.__ice_client.get_ice_entry(ice_id)
            self.__ice_entries[ice_id] = ice_entry

        return self.__ice_entries[ice_id]

    def __get_parts(self, plasmid_id):
        ''''Get parts from plasmid id.'''
        ice_entry = self.get_ice_entry(plasmid_id)

        part_ids = [part['id']
                    for part in ice_entry.get_metadata()['linkedParts']]

        return [self.get_ice_entry(part_id) for part_id in part_ids]
