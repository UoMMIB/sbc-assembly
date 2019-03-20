'''
AssemblyGenie (c) University of Manchester 2019

All rights reserved.

@author: neilswainston
'''
from opentrons import labware, robot


def add_plate(plate_df, typ):
    '''Add plate to deck.'''
    empty_slots = _get_empty_slots()
    plate = labware.load(typ, empty_slots[-1], plate_df.name)

    for _, row in plate_df.iterrows():
        plate.children_by_name[row['well']].properties['id'] = row['id']

    return plate


def add_containers(wells_required, typ, contents=None):
    '''Add container to deck.'''
    containers = []
    wells = 0

    while wells < wells_required:
        empty_slots = _get_empty_slots()
        container = labware.load(typ, slot=empty_slots[-1])
        plate_size = len(container.rows) * len(container.cols)
        wells += plate_size

        if contents is not None:
            for well, _id in zip(container.children_by_name, contents):
                container.children_by_name[well].properties['id'] = _id

        containers.append(container)

    return containers


def _get_empty_slots():
    '''Get empty slots.'''
    return [slot for slot, child in robot.deck.children_by_name.items()
            if not child.children_by_name]
