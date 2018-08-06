'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
import sys

from assembly import opt
import pandas as pd


def optimise(df, num_channels=8):
    '''Optimise.'''
    data = []

    plate_rows = 16 if list(df['src_plate_size'])[0] == 384 else 8
    pipette_idx = list(df['src_pipette_idx'])[0]

    group_dfs = {src_col: group_df
                 for src_col, group_df in df.groupby('src_col')}

    row_idxs = [val + pipette_idx for val in range(0,
                                                   plate_rows,
                                                   plate_rows // num_channels)]

    while len(data) < len(df):
        operation = [None] * num_channels

        for head_row in range(num_channels):
            row = None
            target_row = head_row

            while not row:
                row = _get_well(row_idxs[target_row], group_dfs)

                if row:
                    operation[head_row] = row
                    break

                if len(data) + len([v for v in operation if v]) == len(df):
                    break

                target_row = (target_row + 1) % num_channels

        data.extend([val for val in operation if val])

    return pd.DataFrame(data, columns=df.columns)


def _get_well(pos, group_dfs):
    '''Get well.'''
    for _, group_df in group_dfs.items():
        col_df = group_df[group_df['src_row'] == pos]

        if not col_df.empty:
            row = list(col_df.iloc[[0]].values[0])
            group_df.drop(col_df.index[0], inplace=True)
            return row

    return None


def _sort(df, order):
    '''Sort.'''
    sorted_df = df.sort_values(order)
    return opt.score(sorted_df), sorted_df


def main(args):
    '''main method.'''
    df = opt.get_semirandom_wklst(int(args[0]), int(args[1]))
    df = optimise(df)
    df.to_csv(args[2])


if __name__ == '__main__':
    main(sys.argv[1:])
