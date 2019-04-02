'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
from collections import defaultdict
from operator import itemgetter
import sys


class Lcr3Designer():
    '''Class to design LCR v3 assemblies.'''

    def __init__(self, filename):
        self.__filename = filename
        self.__design_parts = self.__get_design_parts()
        self.__parts = self.__get_parts()
        self.__pairs = self.__get_pairs()

    def get_design_parts(self):
        '''Get design parts.'''
        return self.__design_parts

    def get_parts(self):
        '''Get parts.'''
        return self.__parts

    def get_pairs(self):
        '''Get psirs.'''
        return self.__pairs

    def __get_design_parts(self):
        '''Get design parts.'''
        design_parts = defaultdict(list)

        with open(self.__filename) as fle:
            designs = [tuple(line.strip().split(',')) for line in fle]

            for design in designs:
                design_parts[design].append((('', design[0] + 'bb', '')))

                for idx, _id in enumerate(design):
                    if _id not in ['H', 'L', '']:
                        environment = design[idx - 1:idx + 2]

                        part = ('H' if idx > 1 and
                                environment[0] == 'H' else '',
                                environment[1],
                                'L' if len(environment) > 2 and
                                environment[2] == 'L' else '')

                        design_parts[design].append(part)

        return design_parts

    def __get_parts(self):
        '''Get parts.'''
        return sorted(list({part for parts in self.__design_parts.values()
                            for part in parts}), key=itemgetter(1, 0, 2))

    def __get_pairs(self):
        '''Get pairs.'''
        pairs = set()

        for design_part in self.__design_parts.values():
            valid_parts = [[part for part in parts if len(part)]
                           for parts in design_part]

            for idx, part in enumerate(valid_parts[:-1]):
                pairs.add((part[-1], self.__parts[idx + 1][0]))

        return pairs


def main(args):
    '''main method.'''
    designer = Lcr3Designer(args[0])
    design_parts = designer.get_design_parts()
    parts = designer.get_parts()
    pairs = designer.get_pairs()

    for design, prts in design_parts.items():
        print(design, prts)

    print()

    for part in parts:
        print(part)

    print()

    for pair in pairs:
        print(pair)


if __name__ == '__main__':
    main(sys.argv[1:])
