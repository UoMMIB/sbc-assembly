'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=not-an-iterable
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=unsubscriptable-object
from synbiochem.utils import sort

from assembly import plate
from assembly.optimiser import Optimiser
from assembly.utils import get_graph, get_optimal_src_dest
import pandas as pd


class WorklistGenerator(object):
    '''Class to generate worklists.'''

    def __init__(self, ingredients):
        # Get inputs and reagents:
        self.__inputs = set([])
        self.__reagents = set([])
        self.__analyse_ingredients(ingredients)

        # Convert ingredients to graph:
        optim = Optimiser(ingredients)

        self.__graph, self.__roots, self.__vertices = \
            get_graph(optim.get_matrix())

        self.__edges = [e.tuple for e in self.__graph.es]

        self.__worklist = None
        self.__plates = {}

    def get_worklist(self):
        '''Gets worklist and plates.'''
        if not self.__worklist:
            self.__create_worklist()

        return self.__worklist, self.__plates

    def __analyse_ingredients(self, ingredients):
        try:
            for ingredient in ingredients:
                if isinstance(ingredient, tuple) and \
                        len(ingredient) == 3 and \
                        isinstance(ingredient[0], str) and \
                        isinstance(ingredient[1], (int, long, float)) and \
                        isinstance(ingredient[2], bool):
                    if ingredient[2]:
                        self.__reagents.add(ingredient[0])
                    else:
                        self.__inputs.add(ingredient[0])
                else:
                    self.__analyse_ingredients(ingredient)
        except TypeError:
            # If not iterable:
            return

    def __create_worklist(self):
        '''Creates worklist and plates.'''
        data = []

        for root in self.__roots:
            idx = self.__vertices.index(root)
            self.__traverse(self.__graph.vs[idx], 0, data)

        self.__worklist = pd.DataFrame(data)

        self.__write_plates()
        self.__add_locations()

    def __write_plates(self):
        '''Writes plates from worklist.'''
        # Write input plate:
        inpt = \
            self.__worklist.loc[self.__worklist['input']]['src_name'].values

        for val in sort(inpt):
            plate.add_component(val, 'input', False, self.__plates)

        # Write reagents plate:
        reags = \
            self.__worklist.loc[self.__worklist['reagent']]['src_name'].values

        for val in sort(reags):
            plate.add_component(val, 'MastermixTrough', True, self.__plates)

        # Write intermediates:
        intrm = self.__worklist[~(self.__worklist['input']) &
                                ~(self.__worklist['reagent'])]

        for _, row in intrm.sort_values('level', ascending=False).iterrows():
            plate.add_component(row['src_name'], row['level'], False,
                                self.__plates)

            if row['level'] == 0:
                plate.add_component(row['dest_name'], 'output', False,
                                    self.__plates)

    def __add_locations(self):
        '''Add locations to worklist.'''
        locations = self.__worklist.apply(lambda row: self.__get_location(
            row['src_name'], row['dest_name']), axis=1)

        loc_df = locations.apply(pd.Series)
        loc_df.index = self.__worklist.index
        loc_df.columns = ['SourcePlateBarcode', 'SourcePlateWell',
                          'DestinationPlateBarcode', 'DestinationPlateWell']

        self.__worklist = pd.concat([self.__worklist, loc_df], axis=1)
        self.__worklist.sort_values(['level', 'reagent',
                                     'DestinationPlateWell'],
                                    ascending=[False, False, True],
                                    inplace=True)
        self.__worklist.to_csv('worklist.csv', index=False)

    def __get_location(self, src_name, dest_name):
        '''Get location.'''
        srcs = plate.find(self.__plates, src_name)
        dests = plate.find(self.__plates, dest_name)

        return get_optimal_src_dest(srcs, dests)

    def __traverse(self, vertex, level, data):
        '''Traverse tree.'''
        for predecessor in vertex.predecessors():
            vol = self.__graph.es[self.__edges.index(
                (predecessor.index, vertex.index))]['coeff']
            opr = {'src_name': predecessor['name'],
                   'dest_name': vertex['name'],
                   'Volume': vol,
                   'level': level,
                   'input': predecessor['name'] in self.__inputs,
                   'reagent': predecessor['name'] in self.__reagents}
            data.append(opr)
            self.__traverse(predecessor, level + 1, data)
