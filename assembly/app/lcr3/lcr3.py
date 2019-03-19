'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
from collections import defaultdict
import sys


def main(args):
    '''main method.'''
    design_parts = defaultdict(list)

    with open(args[0]) as fle:
        designs = [tuple(line.strip().split(',')) for line in fle]

        for design in designs:
            design_parts[design].append(design[0:1])

            for idx, _id in enumerate(design):
                if _id not in ['H', 'L', '']:
                    environment = design[idx - 1:idx + 2]
                    design_parts[design].append(
                        environment[0
                                    if idx > 1 and environment[0] == 'H'
                                    else 1:
                                    3
                                    if environment[-1] == 'L'
                                    else 2])

    for design, parts in design_parts.items():
        print(design, parts)

    print()

    print(set([part for parts in design_parts.values() for part in parts]))


if __name__ == '__main__':
    main(sys.argv[1:])
