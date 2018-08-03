'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order

import sys

from assembly import opt


def optimise(df):
    '''Optimise.'''
    src_df = df.sort_values(['src_col', 'src_row'])
    dest_df = df.sort_values(['dest_col', 'dest_row'])

    if opt.score(src_df) < opt.score(dest_df):
        return src_df

    return dest_df


def main(args):
    '''main method.'''
    df = optimise.get_semirandom_wklst(int(args[0]), int(args[1]))
    # df = optimise.get_shuffled_wklst(int(args[0]))
    df = optimise(df)
    df.to_csv(args[2])


if __name__ == '__main__':
    main(sys.argv[1:])
