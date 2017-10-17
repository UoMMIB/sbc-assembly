'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-few-public-methods
from assembly import tree_plotter
import pandas as pd


class Optimiser(object):
    '''Recipes optimiser.'''

    def __init__(self, ingredients):
        self.__df = pd.DataFrame()
        self.__intermediates = 1
        self.__get_components(ingredients[0], ingredients[1])
        self.__drop()
        print self.__df

    def optimise(self):
        '''Optimise dataframe.'''
        while True:
            mask = None
            max_match_col = pd.Series(0.0, index=self.__df.index)

            for idx, col1 in enumerate(self.__df.columns):
                for col2 in self.__df[self.__df.columns[idx + 1:]]:
                    match_col = self.__df[col1] * \
                        (self.__df[col1] == self.__df[col2])

                    if sum(match_col.astype(bool)) > \
                            sum(max_match_col.astype(bool)):
                        mask = pd.DataFrame(0.0, columns=self.__df.columns,
                                            index=self.__df.index)
                        mask[col1] = match_col.values
                        max_match_col = match_col

                    if match_col.sum() and (match_col == max_match_col).all():
                        mask[col2] = match_col.values

            if mask is None or max(mask.astype(bool).sum()) < 2:
                break

            self.__add_intermediate(mask, max_match_col)

        print self.__df

    def plot(self):
        '''Plots matrix as graph.'''
        tree_plotter.plot_matrix(self.__df)

    def __get_components(self, comps, vol, dest=None):
        '''Gets components.'''
        if isinstance(comps, str):
            comp_id = comps
            self.__add_row_col(comp_id)
        else:
            comp_id = self.__get_intermediate_name(vol)

            self.__add_row_col(comp_id)

            for comp in comps:
                self.__get_components(comp[0], comp[1], comp_id)

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
        elif comp_id not in self.__df:
            # Add row:
            new_row = pd.Series([0.0] * len(self.__df.columns),
                                index=self.__df.columns)
            new_row.name = comp_id
            self.__df = self.__df.append(new_row)

            # Add col:
            self.__df[comp_id] = pd.Series([0.0] * len(self.__df.index),
                                           index=self.__df.index)

    def __add_intermediate(self, mask, max_match_col):
        '''Adds an intermediate.'''
        self.__df = self.__df - mask
        new_id = self.__get_intermediate_name()
        self.__df[new_id] = max_match_col
        new_row = mask.any().astype(float)
        new_row.name = new_id
        self.__df = self.__df.append(new_row)
        self.__df = self.__df.fillna(0)
        self.__drop()

    def __get_intermediate_name(self, intermediate=True):
        '''Get unique intermediate name.'''
        prefix = 'i' if intermediate else 'p'
        int_id = prefix + str(self.__intermediates)
        self.__intermediates += 1
        return int_id


def main():
    '''main method.'''
    ingredients = (
        (((((('K', 1), ('L', 2)), 3), ('D', 4), ('E', 5), ('F', 6)), 0),
         ((('D', 4), ('E', 5), ('F', 6), ('Y', 10)), 0),
         ((('D', 4), ('E', 5), ('F', 13), ('Z', 14)), 0)
         ), 0)

    optim = Optimiser(ingredients)
    optim.plot()
    optim.optimise()
    optim.plot()


if __name__ == '__main__':
    main()
