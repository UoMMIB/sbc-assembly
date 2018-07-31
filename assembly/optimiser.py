'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import random
import sys
from assembly import plate
import pandas as pd


def optimise(df):
    '''Optimise.'''
    # df.sort_values(['src_col', 'src_row', 'dest_col', 'dest_row'],
    #               inplace=True)

    df = _shuffle(df)

    return df


def _get_random_wklst(num_wells, plate_size=96):
    '''Get random worklist.'''
    data = []

    for src, dest in zip(random.sample(range(0, plate_size), num_wells),
                         random.sample(range(0, plate_size), num_wells)):
        data.append(_get_well_details(src) + _get_well_details(dest))

    cols = ['SourcePlateWell', 'src_idx', 'src_row', 'src_col',
            'DestinationPlateWell', 'dest_idx', 'dest_row', 'dest_col']

    return pd.DataFrame(data, columns=cols)


def _get_well_details(well_idx):
    '''Get well details.'''
    row, col = plate.get_row_col(well_idx)
    return [plate.get_well_name(row, col), well_idx, row, col]


def _shuffle(df):
    '''Shuffle worklist.'''
    new_index = df.index.values
    val = random.choice(new_index)
    new_index = [i for i in new_index if i != val]
    new_index.insert(random.randrange(len(new_index) + 1), val)
    return df.reindex(new_index)


def main(args):
    '''main method.'''
    df = _get_random_wklst(int(args[0]), int(args[1]))
    df = optimise(df)
    df.to_csv(args[2])


if __name__ == '__main__':
    main(sys.argv[1:])
