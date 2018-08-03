'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order

from operator import itemgetter
import sys

from assembly import opt


def optimise(df):
    '''Optimise.'''
    strategies = [['src_col', 'src_row'],
                  ['dest_col', 'dest_row'],
                  ['src_idx'],
                  ['dest_idx']]

    dfs = [_sort(df, strt) for strt in strategies]
    dfs.sort(key=itemgetter(0))

    return dfs[0][1]


def _sort(df, order):
    '''Sort.'''
    sorted_df = df.sort_values(order)
    return opt.score(sorted_df), sorted_df


def main(args):
    '''main method.'''
    df = opt.get_semirandom_wklst(int(args[0]), int(args[1]))
    # df = opt.get_shuffled_wklst(int(args[0]))
    df = optimise(df)
    df.to_csv(args[2])


if __name__ == '__main__':
    main(sys.argv[1:])
