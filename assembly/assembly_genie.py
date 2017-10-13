'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
from assembly.plate import Plate


class AssemblyGenie(object):
    '''AssemblyGenie.'''

    def __init__(self, recipes):
        self.__plates = []
        self.__mappings = []
        self.__recipes = recipes

    def assemble(self):
        '''Assembles a recipe.'''
        for recipe in self.__recipes:
            self.__assemble(recipe)

    def get_plates(self):
        '''Gets plates.'''
        return self.__plates

    def get_mappings(self):
        '''Gets mappings.'''
        return self.__mappings

    def __assemble(self, components, level=0, dest=None):
        '''Recursively assembles a recipe.'''
        plate_idx, well, obj = self.__add(level, components)
        new_dest = (plate_idx, well, obj)
        print str(new_dest) + '\t->\t' + str(dest)

        for component in components[0]:
            if isinstance(component, tuple):
                self.__assemble(component, level + 1, new_dest)

    def __add(self, plate_idx, obj):
        '''Add object to plate.'''
        if plate_idx >= len(self.__plates):
            self.__plates.append(Plate(plate_idx))

        component = obj[0]
        found = self.__find(component)

        if found:
            return tuple(found[0] + [component])

        well = self.__plates[plate_idx].add(component)
        return plate_idx, well, component

    def __find(self, obj):
        '''Finds an object in Plates.'''
        locations = []

        for plate in self.__plates:
            for location in plate.find(obj):
                locations.append([plate.get_id(), location])

        return locations


def main():
    '''main method.'''
    a = (('A', 5), ('B', 7.5))
    b = (('A', 50), ('C', 17.5))
    c = (('A', 35), (b, 27.5))
    p = ((('X', 3), (a, 2), (c, 4)), 0)

    ass_gen = AssemblyGenie([p, (c, 0)])
    ass_gen.assemble()

    for plate in ass_gen.get_plates():
        print plate

    for mapping in ass_gen.get_mappings():
        print mapping


if __name__ == '__main__':
    main()
