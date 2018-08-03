'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order

import random
import sys

from synbiochem.optimisation.sim_ann import SimulatedAnnealer

from assembly import optimise


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
        self.__df.name = self.__orig_df.name
        return self.__df

    def get_values(self):
        '''Get values.'''
        return [self.get_energy()]

    def get_energy(self):
        '''Get energy.'''
        return optimise.score(self.__df)

    def mutate(self):
        '''Mutate.'''
        self.__mut_df = _shuffle(self.__df, 1)
        return optimise.score(self.__mut_df)

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


def optimise(df):
    '''Optimise.'''
    df.sort_values(['src_col', 'dest_col', 'src_row', 'dest_row'],
                   inplace=True)

    solution = WorklistSolution(df)
    thread = WorklistThread(solution)
    thread.start()
    thread.join()

    return solution.get_result()


def _shuffle(df, num_shuffs=1):
    '''Shuffle worklist.'''
    new_index = list(df.index)

    for _ in range(0, num_shuffs):
        idx1, idx2 = random.sample(new_index, 2)
        new_index[idx1], new_index[idx2] = new_index[idx2], new_index[idx1]

    return df.reindex(new_index)


def main(args):
    '''main method.'''
    df = optimise.get_semirandom_wklst(int(args[0]), int(args[1]))
    # df = optimise.get_shuffled_wklst(int(args[0]))
    df = optimise(df)
    df.to_csv(args[2])


if __name__ == '__main__':
    main(sys.argv[1:])
