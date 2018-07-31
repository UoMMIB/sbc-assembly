'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
from itertools import zip_longest
import math
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


def _score(df, channels=8):
    '''Score.'''
    scores = [_score_group(pd.DataFrame([list(row) for row in rows
                                         if row is not None],
                                        columns=df.columns))
              for rows in _grouper(channels, df.values)]

    print(scores)


def _score_group(group_df):
    '''Score group.'''
    score = 0
    head_col = 0
    head_pos = [[row, head_col] for row in range(0, 8)]
    curr_pos = [list(pos) for pos in group_df[['src_row', 'src_col']].values]

    while True:
        # Eliminate wells in correct position (i.e. pick up or dispense:
        head_curr = [list(pair)
                     if (pair[0] != pair[1]) or (pair[1] == [-1, -1])
                     else [pair[0], [-1, -1]]
                     for pair in zip(head_pos, curr_pos)]
        print(head_curr)

        # If all wells have been picked up / dispensed:
        next_idx = float('NaN')

        for idx, pair in enumerate(head_curr):
            if pair[1] != [-1, -1]:
                next_idx = idx
                break

        if math.isnan(next_idx):
            break

        # Move col:
        head_col = head_curr[next_idx][1][1]
        score += abs(head_col - head_curr[next_idx][0][1])

        # Move row:
        head_row_offset = head_curr[next_idx][1][0] - head_curr[next_idx][0][0]
        score += abs(head_row_offset)
        head_pos = [[row + head_row_offset, head_col] for row, _ in head_pos]
        curr_pos[next_idx] = [-1, -1]
        print(score)

    return score


def _grouper(n, iterable, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks.'''
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def main(args):
    '''main method.'''
    df = _get_random_wklst(int(args[0]), int(args[1]))
    df = optimise(df)
    _score(df)
    df.to_csv(args[2])


if __name__ == '__main__':
    main(sys.argv[1:])
