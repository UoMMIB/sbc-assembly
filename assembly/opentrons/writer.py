'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=wrong-import-order
import math
import sys

from opentrons import containers, instruments, robot

from assembly import plate
import pandas as pd


class OpentronsWriter():
    '''Class representing an Opentrons writer.'''

    def __init__(self, rows=4, cols=3):
        self.__deck = plate.Plate('deck', rows=rows, cols=cols)
        self.__tip_racks = None

    def write(self, filename):
        '''Write commands from worklist csv.'''
        wklst_df = pd.read_csv(filename)

        # Add tip-racks:
        self.__add_tip_racks(len(wklst_df))

        plt_names = ['SourcePlateBarcode', 'DestinationPlateBarcode']
        plates = {name: self.__add_plate('96-flat', name)
                  for name in pd.unique(wklst_df[plt_names].values.ravel())}

        #
        pipette = instruments.Pipette(tip_racks=self.__tip_racks)

        # commands
        for _, row in wklst_df.iterrows():
            pipette.transfer(row['Volume'],
                             plates[row['SourcePlateBarcode']].wells(
                                 row['SourcePlateWell']),
                             plates[row['DestinationPlateBarcode']].wells(
                                 row['DestinationPlateWell']))

    def __add_tip_racks(self, len_worklist, typ='tiprack-200ul'):
        '''Add tipracks to deck.'''
        plt = self.__add_plate(typ, 'tiprack_0')
        plt_size = len(plt.rows) * len(plt.cols)

        self.__tip_racks = [plt] + \
            [self.__add_plate(typ, 'tiprack_' + str(idx))
             for idx in range(1, math.ceil(len_worklist / plt_size))]

    def __add_plate(self, typ, name):
        '''Add plate to deck.'''
        pos = self.__deck.add(name)
        return containers.load(typ, pos, name)


def main(args):
    '''main method.'''
    writer = OpentronsWriter()
    writer.write(args[0])

    for command in robot.commands():
        print(command)


if __name__ == '__main__':
    main(sys.argv[1:])
