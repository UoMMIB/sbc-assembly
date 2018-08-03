'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
from itertools import zip_longest
import math
import random
import sys

from synbiochem.optimisation.sim_ann import SimulatedAnnealer

from assembly import plate
import pandas as pd


class WorklistSolution():
    '''Class to represent a Worklist for simulated annealing optimisation.'''

    def __init__(self, df):
        self.__orig_df = df
        self.__df = df.copy()
        self.__mut_df = df.copy()

    def init(self):
        '''init.'''
        pass

    def get_query(self):
        '''Get query.'''
        return self.__orig_df

    def get_result(self):
        '''Get result.'''
        return self.__df

    def get_values(self):
        '''Get values.'''
        return [self.get_energy()]

    def get_energy(self):
        '''Get energy.'''
        return score(self.__df)

    def mutate(self):
        '''Mutate.'''
        self.__mut_df = _shuffle(self.__df, 1)
        return score(self.__mut_df)

    def accept(self):
        '''Accept.'''
        self.__df = self.__mut_df

    def reject(self):
        '''Reject.'''
        pass

    def __repr__(self):
        return str(list(self.__df['src_well']))


class WorklistThread(SimulatedAnnealer):
    '''Wraps a Worlist optimisation job into a thread.'''

    def __init__(self, solution, verbose=True):
        SimulatedAnnealer.__init__(
            self, solution, r_temp=2.5, cooling_rate=0.00025, verbose=verbose)


def score(df, channels=8):
    '''Score.'''
    min_score = math.ceil(len(df.index) / 8) * 2

    scores = [_score_group(pd.DataFrame([list(row) for row in rows
                                         if row is not None],
                                        columns=df.columns))
              for rows in _grouper(channels, df.values)]

    return sum(scores) - min_score


def optimise(df):
    '''Optimise.'''
    df.sort_values(['src_col', 'dest_col', 'src_row', 'dest_row'],
                   inplace=True)

    solution = WorklistSolution(df)
    thread = WorklistThread(solution)
    thread.start()
    thread.join()

    return solution.get_result()


def _get_shuffled_wklst(num_wells):
    '''Get shuffled worklist.'''
    idx = list(range(0, num_wells))
    df = _get_wklst(idx, idx)
    return df.sample(frac=1)


def _get_semirandom_wklst(num_wells, plate_size=96):
    '''Get semi-random worklist.'''
    idxs = random.sample(range(0, plate_size), num_wells)
    return _get_wklst(idxs, idxs)


def _get_random_wklst(num_wells, plate_size=96):
    '''Get random worklist.'''
    src_idxs = random.sample(range(0, plate_size), num_wells)
    dest_idxs = random.sample(range(0, plate_size), num_wells)
    return _get_wklst(src_idxs, dest_idxs)


def _get_wklst(src_idxs, dest_idxs):
    '''Get worklist.'''
    data = []

    for src, dest in zip(src_idxs, dest_idxs):
        data.append(_get_well_details(src) + _get_well_details(dest))

    cols = ['src_well', 'src_idx', 'src_row', 'src_col',
            'dest_well', 'dest_idx', 'dest_row', 'dest_col']

    return pd.DataFrame(data, columns=cols)


def _get_well_details(well_idx):
    '''Get well details.'''
    row, col = plate.get_row_col(well_idx)
    return [plate.get_well_name(row, col), well_idx, row, col]


def _shuffle(df, num_shuffs=1):
    '''Shuffle worklist.'''
    new_index = list(df.index)

    for _ in range(0, num_shuffs):
        idx1, idx2 = random.sample(new_index, 2)
        new_index[idx1], new_index[idx2] = new_index[idx2], new_index[idx1]

    return df.reindex(new_index)


def _score_group(group_df):
    '''Score group.'''
    return _score_cols(group_df, ['src_row', 'src_col']) + \
        _score_cols(group_df, ['dest_row', 'dest_col'])


def _score_cols(group_df, columns):
    '''Score group by either src or dest (specified by columns).'''
    score = 0
    head_col = 0
    head_pos = [[row, head_col] for row in range(0, 8)]
    curr_pos = [list(pos) for pos in group_df[columns].values]

    while True:
        # Eliminate wells in correct position (i.e. pick up or dispense:
        head_curr = [list(pair)
                     if (pair[0] != pair[1]) or (pair[1] == [-1, -1])
                     else [pair[0], [-1, -1]]
                     for pair in zip(head_pos, curr_pos)]

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

    return score


def _grouper(n, iterable, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks.'''
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def main(args):
    '''main method.'''
    df = _get_semirandom_wklst(int(args[0]), int(args[1]))
    # df = _get_shuffled_wklst(int(args[0]))
    df = optimise(df)
    df.to_csv(args[2])


if __name__ == '__main__':
    main(sys.argv[1:])
