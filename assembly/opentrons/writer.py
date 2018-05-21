'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import math
import sys

from opentrons import containers, instruments, robot

from assembly import plate
import pandas as pd


def write(filename):
    '''Write commands from worklist csv.'''
    worklist_df = pd.read_csv(filename)

    deck = plate.Plate('deck', rows=5, cols=3)

    tip_racks = _add_tip_racks(deck, len(worklist_df))

    plt_names = ['SourcePlateBarcode', 'DestinationPlateBarcode']
    plates = {name: _add_plate(deck, '96-flat', name)
              for name in pd.unique(worklist_df[plt_names].values.ravel('K'))}

    # pipettes
    pipette = instruments.Pipette(
        axis='b', max_volume=200, tip_racks=tip_racks)

    # commands
    for _, row in worklist_df.iterrows():
        pipette.transfer(row['Volume'],
                         plates[row['SourcePlateBarcode']].wells(
                             row['SourcePlateWell']),
                         plates[row['DestinationPlateBarcode']].wells(
                             row['DestinationPlateWell']))


def _add_tip_racks(deck, len_worklist, typ='tiprack-200ul'):
    '''Add tipracks to deck.'''
    plt = _add_plate(deck, typ, 'tiprack_0')
    plt_size = len(plt.rows) * len(plt.cols)

    return [plt] + [_add_plate(deck, typ, 'tiprack_' + str(idx))
                    for idx in range(1, math.ceil(len_worklist / plt_size))]


def _add_plate(deck, typ, name):
    '''Add plate to deck.'''
    pos = deck.add(name)
    plate = containers.load(typ, pos, name)
    return plate


def main(args):
    '''main method.'''
    write(args[0])

    for command in robot.commands():
        print(command)


if __name__ == '__main__':
    main(sys.argv[1:])
