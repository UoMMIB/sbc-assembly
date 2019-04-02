'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=too-many-instance-attributes
from collections import defaultdict
from operator import itemgetter
import sys
from synbiochem.utils import ice_utils, seq_utils

_H_PRIMER = 'ATAGTTCCCTTCACGATAGCCG'
_L_PRIMER = 'TGCTGGATACGACGCTCTACTC'


class Lcr3Designer():
    '''Class to design LCR v3 assemblies.'''

    def __init__(self, filename, ice_params, primer_melt_temp=60.0):
        self.__filename = filename
        self.__primer_melt_temp = primer_melt_temp

        self.__ice_client_fact = ice_utils.ICEClientFactory()
        self.__ice_client = \
            self.__ice_client_fact.get_ice_client(ice_params['url'],
                                                  ice_params['username'],
                                                  ice_params['password'])

        self.__primers = defaultdict(dict)
        self.__seqs = {}
        self.__design_parts = self.__get_design_parts()
        self.__part_primers = self.__get_part_primers()
        self.__pairs = self.__get_pairs()

    def close(self):
        '''Close.'''
        self.__ice_client_fact.close()

    def get_design_parts(self):
        '''Get design parts.'''
        return self.__design_parts

    def get_part_primers(self):
        '''Get part primers.'''
        return self.__part_primers

    def get_pairs(self):
        '''Get psirs.'''
        return self.__pairs

    def __get_design_parts(self):
        '''Get design parts.'''
        design_parts = defaultdict(list)

        with open(self.__filename) as fle:
            designs = [tuple(line.strip().split(',')) for line in fle]

            for design in designs:
                design_parts[design].append(((design[0] + 'bb', '', '')))

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

    def __get_part_primers(self):
        '''Get part primers.'''
        parts = sorted(list({part for parts in self.__design_parts.values()
                             for part in parts}), key=itemgetter(1, 0, 2))

        return {part: self.__get_primers_for_part(part) for part in parts}

    def __get_pairs(self):
        '''Get pairs.'''
        pairs = set()

        for design_part in self.__design_parts.values():
            condensed_parts = [_condense_part(part)
                               for part in design_part]

            for idx, condensed_part in enumerate(condensed_parts[:-1]):
                pairs.add((condensed_part[-1], condensed_parts[idx + 1][0]))

        return pairs

    def __get_primers_for_part(self, part):
        '''Get primers.'''
        return (self.__get_primer(part, False),
                self.__get_primer(part, True))

    def __get_primer(self, part, forward):
        '''Get primer from ICE id.'''
        primer = None

        if part not in self.__primers[forward]:
            if forward:
                if part[0] == 'H':
                    return _H_PRIMER
                if part[0] == 'Lbb':
                    return None
                if part[0] == 'Hbb':
                    return None
            else:
                if part[2] == 'L':
                    return _L_PRIMER
                if part[0] == 'Lbb':
                    return None
                if part[0] == 'Hbb':
                    return None

            # else:
            seq = self.__get_seq(part[1])
            primer = seq_utils.get_seq_by_melt_temp(
                seq, self.__primer_melt_temp, forward)[0]

            self.__primers[forward][part] = primer

        return self.__primers[forward][part]

    def __get_seq(self, ice_id):
        '''Get seq.'''
        if ice_id not in self.__seqs:
            self.__seqs[ice_id] = \
                self.__ice_client.get_ice_entry(ice_id).get_seq()

        return self.__seqs[ice_id]


def _condense_part(part):
    '''Condense part, removing 'empty' components.'''
    return [component for component in part if len(component)]


def main(args):
    '''main method.'''
    designer = Lcr3Designer(args[0],
                            {'url': args[1],
                             'username': args[2],
                             'password': args[3]})

    design_parts = designer.get_design_parts()
    part_primers = designer.get_part_primers()
    pairs = designer.get_pairs()
    designer.close()

    for design, prts in design_parts.items():
        print(design, prts)

    print()

    for part, primers in part_primers.items():
        print(part, primers)

    print()

    for pair in pairs:
        print(pair)


if __name__ == '__main__':
    main(sys.argv[1:])
