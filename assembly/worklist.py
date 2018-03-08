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
from assembly.utils import get_optimal_src_dest, get_roots
import pandas as pd


class WorklistGenerator(object):
    '''Class to generate worklists.'''

    def __init__(self, graph):
        self.__graph = graph
        self.__worklist = None
        self.__plates = {}

    def get_worklist(self):
        '''Gets worklist and plates.'''
        if not self.__worklist:
            self.__create_worklist()

        return self.__worklist, self.__plates

    def __create_worklist(self):
        '''Creates worklist and plates.'''
        data = []

        for root in get_roots(self.__graph):
            self.__traverse(root, 0, data)

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

        # Write products:
        for _, row in self.__worklist.iterrows():
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
        for pre in vertex.predecessors():
            edge_idx = self.__graph.get_eid(pre.index, vertex.index)
            edge = self.__graph.es[edge_idx]
            vol = edge['vol']
            opr = {'src_name': pre['name'],
                   'dest_name': vertex['name'],
                   'Volume': vol,
                   'level': level,
                   'input': not pre.indegree() and not pre['is_reagent'],
                   'reagent': pre['is_reagent']}
            data.append(opr)
            self.__traverse(pre, level + 1, data)
