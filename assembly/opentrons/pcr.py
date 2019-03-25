'''
AssemblyGenie (c) University of Manchester 2019

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
# pylint: disable=ungrouped-imports
# pylint: disable=wrong-import-order
from collections import defaultdict
from functools import cmp_to_key

from opentrons import instruments, labware

from assembly.opentrons import utils
import pandas as pd

_DEFAULT_VOL = {'water': 20.0,
                'primer': 5.0,
                'internal': 1.0,
                'mm': 3.0}


class PcrWriter():
    '''Class representing an PCR writer.'''

    def __init__(self, src_plate_dfs, products, vol=None):
        if vol is None:
            vol = _DEFAULT_VOL

        self.__plt_mgr = utils.PlateManager()
        self.__products = products

        fragments = sorted(list({fragment
                                 for product in products.values()
                                 for fragment in product}),
                           key=cmp_to_key(utils.compare_items))

        self.__fragment_df = pd.DataFrame(columns=products.keys(),
                                          index=['water'] + fragments + ['mm'])

        for product_id, frags in self.__products.items():
            self.__fragment_df[product_id].loc['water'] = vol['water']
            self.__fragment_df[product_id].loc[[
                frags[0], frags[-1]]] = vol['primer']
            self.__fragment_df[product_id].loc[frags[1:-1]] = vol['internal']
            self.__fragment_df[product_id].loc['mm'] = vol['mm']

        self.__fragment_df = self.__fragment_df.T

        # Add trash:
        self.__trash = labware.load('trash-box', '1')

        # Add tipracks:
        tip_racks = \
            self.__plt_mgr.add_containers('opentrons-tiprack-300ul',
                                          (len(self.__fragment_df.columns) -
                                           3 // 8) + 1  # oligos
                                          + 16)  # water and mastermix

        # Add water-trough:
        self.__plt_mgr.add_container('trough-12row', ['water'] * 8,
                                     name='water')

        # Add master-mix:
        self.__plt_mgr.add_container('96-PCR-flat', ['mm'] * 8,
                                     name='reagents')

        # Add plates:
        self.__plt_mgr.add_containers('96-PCR-flat',
                                      self.__products.keys())

        for src_plate_df in src_plate_dfs:
            self.__plt_mgr.add_plate_df('96-PCR-flat', src_plate_df)

        # Add pipettes:
        self.__single_pipette = \
            instruments.P300_Single(mount='left', tip_racks=tip_racks)

        self.__multi_pipette = \
            instruments.P50_Multi(mount='right', tip_racks=tip_racks)

    def write(self):
        '''Write commands.'''
        for comp_id in self.__fragment_df:
            src_plates, src_wells = \
                zip(*self.__plt_mgr.get_plate_well([comp_id]))

            products = self.__fragment_df[comp_id]

            if products.isnull().any():
                # Oligo:
                products = products[~products.isnull()]
                plate_well_vols = self.__get_plate_well_vol(products)

                for plate, well_vols in plate_well_vols.items():
                    well_vols = list(zip(*well_vols))

                    self.__single_pipette.transfer(
                        well_vols[1],
                        src_plates[0].wells(src_wells[0]),
                        plate.wells(list(well_vols[0])))
            else:
                # Reagent:
                pass

    def __get_plate_well_vol(self, ids_vols):
        '''Get well / plate / volumes.'''
        plate_well_vol = defaultdict(list)
        plate_wells = self.__plt_mgr.get_plate_well(ids_vols.index)

        for plate_well, vol in zip(plate_wells, ids_vols):
            plate_well_vol[plate_well[0]].append((plate_well[1], vol))

        return plate_well_vol
