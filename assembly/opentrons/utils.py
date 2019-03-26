'''
AssemblyGenie (c) University of Manchester 2019

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from collections import defaultdict
import re

from opentrons import labware, robot


class PlateManager():
    '''Class to manage plates.'''

    def __init__(self):
        self.__id_plate_wells = defaultdict(list)

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
            self.__id_plate_wells[_id].append((container, well))

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

    def get_plate_wells(self, comp_ids):
        '''Get plate / wells for component id.'''
        return [self.__id_plate_wells[comp_id] for comp_id in comp_ids]


def compare_items(item1, item2):
    '''Compare items.'''
    regex = r'(\d+)(\D+)?(\d+)?'

    match1 = re.match(regex, item1)
    match2 = re.match(regex, item2)

    return _compare_items(match1, match2)


def _compare_items(match1, match2, index=1):
    '''Compare items.'''
    try:
        val1 = int(match1[index])
        val2 = int(match2[index])
    except (TypeError, ValueError):
        val1 = match1[index]
        val2 = match2[index]

    if not val1 and not val2:
        return 0

    if not val1:
        return -1

    if not val2:
        return 1

    if val1 > val2:
        return 1

    if val1 < val2:
        return -1

    return _compare_items(match1, match2, index + 1)


def _get_empty_slots():
    '''Get empty slots.'''
    return [slot for slot, child in robot.deck.children_by_name.items()
            if not child.children_by_name]
