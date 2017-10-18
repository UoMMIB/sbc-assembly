'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=unsubscriptable-object
from assembly.utils import get_graph


class WorklistGenerator(object):
    '''Class to generate worklists.'''

    def __init__(self, df):
        self.__graph, self.__roots, self.__vertices = get_graph(df)
        self.__edges = [e.tuple for e in self.__graph.es]
        self.__worklist = None

    def get_worklist(self):
        '''Gets worklist.'''
        if self.__worklist is None:
            self.__create_worklist()

        return self.__worklist

    def __create_worklist(self):
        '''Creates worklist.'''
        self.__worklist = []

        for root in self.__roots:
            idx = self.__vertices.index(root)
            self.__traverse(self.__graph.vs[idx], 0)

        self.__worklist.sort(key=lambda row: (-row[3], row[0], row[1]))

    def __traverse(self, vertex, level):
        '''Traverse tree.'''
        for predecessor in vertex.predecessors():
            self.__worklist.append([predecessor['name'],
                                    vertex['name'],
                                    self.__get_vol(predecessor, vertex),
                                    level])
            self.__traverse(predecessor, level + 1)

    def __get_vol(self, src, dst):
        '''Return volume.'''
        edge = self.__graph.es[self.__edges.index((src.index, dst.index))]
        return edge['coeff']
