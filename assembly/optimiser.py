'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
import uuid

import pandas as pd


def optimise(ingredients):
    '''Optimise dataframe.'''
    df = _init(ingredients)

    while True:
        mask = None
        max_match_col = pd.Series(0.0, index=df.index)

        for idx, col1 in enumerate(df.columns):
            for col2 in df[df.columns[idx + 1:]]:
                match_col = df[col1] * (df[col1] == df[col2])

                if sum(match_col.astype(bool)) > \
                        sum(max_match_col.astype(bool)):
                    mask = pd.DataFrame(0.0, columns=df.columns,
                                        index=df.index)
                    mask[col1] = match_col.values
                    # mask[col2] = match_col.values
                    max_match_col = match_col

                if (match_col == max_match_col).all():
                    mask[col2] = match_col.values

        if mask is None or max(mask.astype(bool).sum()) < 2:
            break

        df = _add_intermediate(df, mask, max_match_col)

    return df


def _init(ingredients):
    '''Initialise dataframe.'''
    components = set()

    for product, comps in ingredients.iteritems():
        components.add(product)
        components.update(comps)

    df = pd.DataFrame(0.0, columns=components, index=components)

    for product, comps in ingredients.iteritems():
        for comp in comps:
            df[product][comp] = 1

    return _drop(df)


def _drop(df):
    '''Drop empty columns and rows.'''
    df = df[df.columns[(df != 0).any()]]
    return df[(df.T != 0).any()]


def _add_intermediate(df, mask, max_match_col):
    '''Adds an intermediate.'''
    df = df - mask
    new_id = str(uuid.uuid4())
    df[new_id] = max_match_col
    new_row = mask.any().astype(float)
    new_row.name = new_id
    df = df.append(new_row)
    df = df.fillna(0)
    return _drop(df)


def main():
    '''main method.'''
    ingredients = {'A': ['X', 'D', 'E', 'F'],
                   'B': ['D', 'E', 'F', 'Y'],
                   'C': ['D', 'E', 'F', 'Z']}

    df = optimise(ingredients)
    print df


if __name__ == '__main__':
    main()
