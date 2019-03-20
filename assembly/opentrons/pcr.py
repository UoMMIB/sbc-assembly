'''
AssemblyGenie (c) University of Manchester 2019

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from collections import defaultdict

from opentrons import instruments, labware

from assembly.opentrons import utils


class PcrWriter():
    '''Class representing an PCR writer.'''

    def __init__(self, src_plate_dfs, products):
        self.__products = products
        self.__fragments = defaultdict(list)

        for product_id, product in products.items():
            for fragment in product:
                self.__fragments[fragment].append(product_id)

        # Add trash:
        self.__trash = labware.load('trash-box', '1')

        # Add tipracks:
        tip_racks = \
            utils.add_containers((len(self.__fragments) - 1 // 8) + 1  # oligos
                                 + 16,  # water and mastermix
                                 typ='opentrons-tiprack-300ul')

        # Add plates:
        self.__product_plates = utils.add_containers(len(self.__products),
                                                     '96-PCR-flat',
                                                     self.__products.keys())

        self.__src_plates = [utils.add_plate(src_plate_df, '96-PCR-flat')
                             for src_plate_df in src_plate_dfs]

        # Add pipettes:
        self.__single_pipette = \
            instruments.P300_Single(mount='left', tip_racks=tip_racks)

        self.__multi_pipette = \
            instruments.P50_Multi(mount='right', tip_racks=tip_racks)

    def write(self):
        '''Write commands.'''
        for _id, product in self.__products.items():
            print(_id, product)

    def _add_fragments(self):
        '''Add fragments.'''
        for fragment in self.__fragments:
            self.__single_pipette.pick_up_tip()
            self.__single_pipette.drop_tip()
