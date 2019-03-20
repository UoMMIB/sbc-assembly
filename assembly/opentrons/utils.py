'''
AssemblyGenie (c) University of Manchester 2019

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from opentrons import labware, robot


class PlateManager():
    '''Class to manage plates.'''

    def __init__(self):
        self.__id_plate_wells = {}

    def add_plate_df(self, typ, plate_df, name=None):
        '''Add single plate.'''
        return self.add_container(typ, plate_df['id'], plate_df['well'], name)

    def add_container(self, typ, ids, wells=None, name=None):
        '''Add container to deck.'''
        empty_slots = _get_empty_slots()
        container = labware.load(typ, empty_slots[-1], name)

        if wells is None:
            wells = list(container.children_by_name.keys())[:len(ids)]

        for well, _id in zip(wells, ids):
            # container.children_by_name[well].properties['id'] = _id
            self.__id_plate_wells[_id] = (container, well)

        return container

    def add_containers(self, typ, ids, name=None):
        '''Add container to deck.'''
        if isinstance(ids, int):
            ids = [None] * ids

        containers = []
        wells = 0

        while wells < len(ids):
            container = self.add_container(typ, ids, name=name)
            plate_size = len(container.rows) * len(container.cols)
            wells += plate_size
            containers.append(container)

        return containers

    def get_plate_well(self, comp_ids):
        '''Get plate, well for component id.'''
        plate_wells = [self.__id_plate_wells[comp_id] for comp_id in comp_ids]
        assert len(plate_wells) == len(comp_ids)
        return plate_wells


def _get_empty_slots():
    '''Get empty slots.'''
    return [slot for slot, child in robot.deck.children_by_name.items()
            if not child.children_by_name]
