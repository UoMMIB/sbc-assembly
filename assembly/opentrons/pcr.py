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

    def __init__(self, src_plate_dfs, recipes, vol=None):
        if vol is None:
            vol = _DEFAULT_VOL

        self.__plt_mgr = utils.PlateManager()
        self.__recipe_df = _get_recipe_df(recipes, vol)

        # Add trash:
        self.__trash = labware.load('trash-box', '1')

        # Add tipracks:
        tip_racks = \
            self.__plt_mgr.add_containers('opentrons-tiprack-300ul',
                                          (len(self.__recipe_df.columns) -
                                           3 // 8) + 1  # oligos
                                          + 16)  # water and mastermix

        # Add water-trough:
        self.__plt_mgr.add_container('trough-12row', ['water'] * 8,
                                     name='water')

        # Add master-mix:
        self.__plt_mgr.add_container('96-PCR-flat', ['mm'] * 8,
                                     name='reagents')

        # Add plates:
        self.__plt_mgr.add_containers('96-PCR-flat', self.__recipe_df.index)

        for src_plate_df in src_plate_dfs:
            self.__plt_mgr.add_plate_df('96-PCR-flat', src_plate_df)

        # Add pipettes:
        self.__single_pipette = \
            instruments.P300_Single(mount='left', tip_racks=tip_racks)

        self.__multi_pipette = \
            instruments.P50_Multi(mount='right', tip_racks=tip_racks)

    def write(self):
        '''Write commands.'''
        for comp_id in self.__recipe_df:
            src_plate_wells = self.__plt_mgr.get_plate_wells([comp_id])[0]
            src_plate = src_plate_wells[0][0]

            products = self.__recipe_df[comp_id]
            products = products[~products.isnull()]
            dest_plate_well_vols = self.__get_plate_well_vol(products)

            for dest_plate, dest_well_vols in dest_plate_well_vols.items():
                dest_well, vols = list(zip(*dest_well_vols))

                if len(src_plate_wells) == 1:
                    # Single pipette:
                    self.__single_pipette.distribute(
                        list(vols),
                        src_plate.wells(src_plate_wells[0][1]),
                        dest_plate.wells(list(dest_well)))
                else:
                    # Multi-pipette:
                    self.__multi_pipette.pick_up_tip()

                    for idx in range(0, len(dest_well), 8):
                        self.__multi_pipette.distribute(
                            list(vols[idx:idx + 8]),
                            src_plate.wells(
                                [src_plate_well[1]
                                 for src_plate_well in src_plate_wells]),
                            dest_plate.wells(list(dest_well[idx:idx + 8])),
                            new_tip='never')

                    self.__multi_pipette.drop_tip()

    def __get_plate_well_vol(self, ids_vols):
        '''Get well / plate / volumes.'''
        plate_well_vol = defaultdict(list)
        all_plate_wells = self.__plt_mgr.get_plate_wells(ids_vols.index)

        for plate_wells, vol in zip(all_plate_wells, ids_vols):
            for plate_well in plate_wells:
                plate_well_vol[plate_well[0]].append((plate_well[1], vol))

        return plate_well_vol


def _get_recipe_df(recipes, vol):
    '''Get recipe DataFrame.'''
    ingredients = sorted(list({ingredient
                               for recipe in recipes.values()
                               for ingredient in recipe}),
                         key=cmp_to_key(utils.compare_items))

    recipe_df = pd.DataFrame(columns=recipes.keys(),
                             index=['water'] + ingredients + ['mm'])

    for product_id, frags in recipes.items():
        recipe_df[product_id].loc['water'] = vol['water']
        recipe_df[product_id].loc[[frags[0], frags[-1]]] = vol['primer']
        recipe_df[product_id].loc[frags[1:-1]] = vol['internal']
        recipe_df[product_id].loc['mm'] = vol['mm']

    return recipe_df.T
