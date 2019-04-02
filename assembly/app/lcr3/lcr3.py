'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
from collections import defaultdict
from operator import itemgetter
import sys


def get_design_parts(filename):
    '''Get design parts.'''
    design_parts = defaultdict(list)

    with open(filename) as fle:
        designs = [tuple(line.strip().split(',')) for line in fle]

        for design in designs:
            design_parts[design].append((('', design[0] + 'bb', '')))

            for idx, _id in enumerate(design):
                if _id not in ['H', 'L', '']:
                    environment = design[idx - 1:idx + 2]

                    part = ('H' if idx > 1 and environment[0] == 'H' else '',
                            environment[1],
                            'L' if len(environment) > 2 and
                            environment[2] == 'L' else '')

                    design_parts[design].append(part)

    return design_parts


def get_parts(design_parts):
    '''Get parts.'''
    return sorted(list({part for parts in design_parts.values()
                        for part in parts}), key=itemgetter(1, 0, 2))


def get_pairs(design_parts, parts):
    '''Get pairs.'''
    pairs = set()

    for design_part in design_parts.values():
        valid_parts = [[part for part in parts if len(part)]
                       for parts in design_part]

        for idx, part in enumerate(valid_parts[:-1]):
            pairs.add((part[-1], parts[idx + 1][0]))

    return pairs


def main(args):
    '''main method.'''
    design_parts = get_design_parts(args[0])
    parts = get_parts(design_parts)
    pairs = get_pairs(design_parts, parts)

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
