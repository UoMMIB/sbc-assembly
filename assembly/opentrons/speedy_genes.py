'''
AssemblyGenie (c) University of Manchester 2019

All rights reserved.

@author: neilswainston
'''
# pylint: disable=wrong-import-order
from itertools import combinations
import sys

from opentrons import robot

from assembly.opentrons import pcr
import pandas as pd


def _get_variants(block, num_variant):
    '''Get variants.'''
    variants = list(combinations(block, num_variant))

    return [['%sv' % oligo if oligo in variant else oligo
             for oligo in block]
            for variant in variants]


def main(args):
    '''main method.'''
    plate = pd.read_csv(args[0])
    plate.name = args[0]

    blocks = [['1', '2', '3', '4', '5', '6', '7', '8'],
              ['9', '10', '11', '12', '13', '14', '15', '16']]

    num_variants = [0, 1, 2]

    designs = [[[block_idx + 1, num_var, var_idx + 1, var]
                for num_var, lst in enumerate(
                    [_get_variants(block, num_variant)
                     for num_variant in num_variants])
                for var_idx, var in enumerate(lst)]
               for block_idx, block in enumerate(blocks)]

    writer = pcr.PcrWriter([plate],
                           {'_'.join(map(str, product[:3])): product[3]
                            for design in designs
                            for product in design})
    writer.write()

    for command in robot.commands():
        print(command)


if __name__ == '__main__':
    main(sys.argv[1:])
