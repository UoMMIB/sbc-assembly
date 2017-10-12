'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
import sys

from assembly.plate import Plate


class AssemblyGenie(object):
    '''AssemblyGenie.'''

    def __init__(self, recipes):
        self.__plates = []
        self.__recipes = recipes

    def assemble(self):
        '''Assembles a recipe.'''
        for recipe in self.__recipes:
            self.__assemble(recipe)

    def get_plates(self):
        '''Gets plates.'''
        return self.__plates

    def __assemble(self, recipe, level=0):
        '''Recursively assembles a recipe.'''
        print str(self.__add(level, recipe)) + '\t' + str(recipe)

        for term in recipe[0]:
            if isinstance(term, tuple):
                self.__assemble(term, level + 1)

    def __add(self, plate_idx, obj):
        '''Add object to plate.'''
        if plate_idx >= len(self.__plates):
            self.__plates.append(Plate(plate_idx))

        component = obj[0]
        found = self.__find(component)

        if found:
            return found[0]

        row, col = self.__plates[plate_idx].add(component)
        return plate_idx, row, col

    def __find(self, obj):
        '''Finds an object in Plates.'''
        locations = []

        for plate in self.__plates:
            for location in plate.find(obj):
                locations.append([plate.get_id(), location])

        return locations


def main(args):
    '''main method.'''
    a = (('A', 5), ('B', 7.5))
    b = (('A', 50), ('C', 17.5))
    c = (('A', 35), (b, 27.5))
    p = ((('X', 3), (a, 2), (c, 4)), 0)

    ass_gen = AssemblyGenie([p, (c, 0)])
    ass_gen.assemble()

    for plate in ass_gen.get_plates():
        print plate


if __name__ == '__main__':
    main(sys.argv[1:])
