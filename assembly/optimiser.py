'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
import pandas as pd


class Optimiser(object):
    '''Recipes optimiser.'''

    def __init__(self, ingredients):
        self.__df = pd.DataFrame()
        self.__intermediates = 1
        self.__get_components(ingredients[0], ingredients[1])
        self.__drop()
        print self.__df

    def __get_components(self, comps, vol, dest=None):
        '''Gets components.'''
        print str(comps) + '\t' + str(vol) + '\t' + str(dest)

        if isinstance(comps, str):
            comp_id = comps
            self.__add_row_col(comp_id)
        else:
            comp_id = '_i' + str(self.__intermediates)
            self.__intermediates += 1

            self.__add_row_col(comp_id)

            for comp in comps:
                try:
                    self.__get_components(comp[0], comp[1], comp_id)
                except IndexError, e:
                    print e

        if dest:
            self.__df[dest][comp_id] = vol

    def __drop(self):
        '''Drop empty columns and rows.'''
        self.__df = self.__df[self.__df.columns[(self.__df != 0).any()]]
        self.__df = self.__df[(self.__df.T != 0).any()]

    def __add_row_col(self, comp_id):
        '''Add new row and column.'''
        if self.__df.empty:
            self.__df[comp_id] = pd.Series([0.0], index=[comp_id])
        elif comp_id not in self._Optimiser__df:
            # Add row:
            new_row = pd.Series([0.0] * len(self.__df.columns),
                                index=self.__df.columns)
            new_row.name = comp_id
            self.__df = self.__df.append(new_row)

            # Add col:
            self.__df[comp_id] = pd.Series([0.0] * len(self.__df.index),
                                           index=self.__df.index)


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
                    max_match_col = match_col

                if match_col.sum() and (match_col == max_match_col).all():
                    mask[col2] = match_col.values

        if mask is None or max(mask.astype(bool).sum()) < 2:
            break

        df = _add_intermediate(df, mask, max_match_col)

    return df


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
    ingredients = (
        (((((('K', 1), ('L', 2)), 3), ('D', 4), ('E', 5), ('F', 6)), 0),
         ((('D', 7), ('E', 8), ('F', 9), ('Y', 10)), 0),
         ((('D', 11), ('E', 12), ('F', 13), ('Z', 14)), 0)
         ), 0)

    optim = Optimiser(ingredients)
    # df = optimise(ingredients)


if __name__ == '__main__':
    main()
