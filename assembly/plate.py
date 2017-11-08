'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
import pandas as pd


class Plate(object):
    '''Class to represent a well plate.'''

    def __init__(self, plate_id, rows=8, cols=12, col_ord=False):
        self.__plate_id = plate_id
        self.__plate = pd.DataFrame(index=[chr(r + ord('A'))
                                           for r in range(0, rows)],
                                    columns=range(1, cols + 1))

        self.__col_ord = col_ord
        self.__next = 0

    def get_id(self):
        '''Get id.'''
        return self.__plate_id

    def shape(self):
        '''Get plate shape.'''
        return self.__plate.shape

    def set(self, obj, row, col):
        '''Set object at a given row, col.'''
        self.__next = max(self.__next, self.get_idx(row, col) + 1)
        self.__plate[col + 1][row] = obj

    def get(self, row, col):
        '''Get object at a given row, col.'''
        return self.__plate[col + 1][row]

    def get_by_well(self, well):
        '''Get by well, e.g. by C12.'''
        return self.get(ord(well[0]) - ord('A'), int(well[1:]) - 1)

    def add(self, obj):
        '''Adds an object to the next well.'''
        return self.__set(obj, self.__next)

    def find(self, obj):
        '''Finds an object.'''
        wells = []

        for col in self.__plate:
            resp = self.__plate[col][self.__plate[col] == obj]

            for row in resp.index.values:
                wells.append(row + str(col))

        return wells

    def get_row_col(self, idx):
        '''Map idx to well, column ordered.'''
        rows, cols = self.__plate.shape

        if self.__col_ord:
            return (idx / cols), (idx % cols)

        return (idx % rows), (idx / rows)

    def get_idx(self, row, col):
        '''Map idx to well, column ordered.'''
        rows, cols = self.__plate.shape

        if self.__col_ord:
            return row * cols + col

        return col * rows + row

    def __set(self, obj, idx):
        '''Sets an object in the given well.'''
        row, col = self.get_row_col(idx)
        self.set(obj, row, col)
        return self.__plate[col + 1].index[row] + str(col + 1)

    def __repr__(self):
        return self.__plate.__repr__()


def write_plates(worklist):
    '''Writes plates from worklist.'''
    plates = {}

    for injection in worklist:
        print injection
        src = injection[0]
        dest = injection[1]
        depth = injection[3]
        _add_component(src, depth, plates)

        if depth == 0:
            _add_component(dest, depth, plates)

    for plate in plates.values():
        print plate


def _add_component(component, plate_id, plates):
    '''Add a component to a plate.'''
    for plate in plates.values():
        if plate.find(component):
            return

    if plate_id not in plates:
        plate = Plate(plate_id)
        plates[plate_id] = plate

    plates[plate_id].add(component)
