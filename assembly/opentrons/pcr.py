'''
AssemblyGenie (c) University of Manchester 2019

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly.opentrons import utils


class PcrWriter():
    '''Class representing an PCR writer.'''

    def __init__(self, src_plate_dfs, products):
        self.__products = products

        self.__oligos = {fragment
                         for product in products
                         for fragment in product}

        self.__tip_racks = \
            utils.add_container((len(self.__oligos) - 1 // 8) + 1  # oligos
                                + 16,  # water and mastermix
                                typ='opentrons-tiprack-300ul')

        self.__product_plates = utils.add_container(len(self.__products),
                                                    '96-PCR-flat')

        self.__src_plates = [utils.add_plate(src_plate_df, '96-PCR-flat')
                             for src_plate_df in src_plate_dfs]

    def write(self):
        '''Write commands.'''
        for product in self.__products:
            print(product)
