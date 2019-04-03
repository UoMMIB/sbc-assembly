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
from assembly.app.lcr3 import overhang


_H_PRIMER = 'ATAGTTCCCTTCACGATAGCCG'
_L_PRIMER = 'TGCTGGATACGACGCTCTACTC'

_HBB_PRIMER_FORW = 'GGATCCAAACTCGAGTAAGG'
_HBB_PRIMER_REV = 'CTTCTTAAAAGATCTTTTGAATTC'
_LBB_PRIMER_FORW = 'GGATCCAAACTCGAGTAAGG'
_LBB_PRIMER_REV = 'CTTCTTAAAAGATCTTTTGAATTC'


class Lcr3Designer():
    '''Class to design LCR v3 assemblies.'''

    def __init__(self, filename, ice_params, primer_melt_temp=60.0,
                 lcr_melt_temp=70.0):
        self.__filename = filename
        self.__primer_melt_temp = primer_melt_temp
        self.__lcr_melt_temp = lcr_melt_temp

        self.__ice_client_fact = ice_utils.ICEClientFactory()
        self.__ice_client = \
            self.__ice_client_fact.get_ice_client(ice_params['url'],
                                                  ice_params['username'],
                                                  ice_params['password'])

        self.__primers = defaultdict(dict)
        self.__primers[True]['Hbb'] = _HBB_PRIMER_FORW
        self.__primers[False]['Hbb'] = _HBB_PRIMER_REV
        self.__primers[True]['Lbb'] = _LBB_PRIMER_FORW
        self.__primers[False]['Lbb'] = _LBB_PRIMER_REV

        self.__domino_parts = defaultdict(dict)
        self.__domino_parts[True]['Hbb'] = '***'
        self.__domino_parts[False]['Hbb'] = '***'
        self.__domino_parts[True]['Lbb'] = '***'
        self.__domino_parts[False]['Lbb'] = '***'

        self.__overhangs = overhang.get_seqs()
        self.__overhang_idx = 0

        self.__seqs = {}
        self.__design_parts = self.__get_design_parts()
        self.__part_primers = self.__get_part_primers()
        self.__pair_dominoes = self.__get_pair_dominoes()

    def close(self):
        '''Close.'''
        self.__ice_client_fact.close()

    def get_design_parts(self):
        '''Get design parts.'''
        return self.__design_parts

    def get_part_primers(self):
        '''Get part primers.'''
        return self.__part_primers

    def get_pair_dominoes(self):
        '''Get pair dominoes.'''
        return self.__pair_dominoes

    def __get_design_parts(self):
        '''Get design parts.'''
        design_parts = defaultdict(list)

        with open(self.__filename) as fle:
            designs = [tuple(line.strip().split(',')) for line in fle]

            for design in designs:
                design_parts[design].append(design[0] + 'bb')

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

    def __get_pair_dominoes(self):
        '''Get dominoes.'''
        pair_dominoes = {}

        for design_part in self.__design_parts.values():
            for idx, part in enumerate(design_part[:-1]):
                pair = (part, design_part[idx + 1])

                if pair not in pair_dominoes:
                    domino = self.__get_domino(pair)
                    pair_dominoes[pair] = domino

        return pair_dominoes

    def __get_primers_for_part(self, part):
        '''Get primers.'''
        return (self.__get_primer(part, True),
                self.__get_primer(part, False))

    def __get_primer(self, part, forward):
        '''Get primer from ICE id.'''
        primer = None

        if part not in self.__primers[forward]:
            if forward and part[0] == 'H':
                return self.__get_next_overhang() + _H_PRIMER
            if not forward and part[2] == 'L':
                return _L_PRIMER + self.__get_next_overhang()

            # else:
            primer = \
                self.__get_subseq(part[1], self.__primer_melt_temp, forward)

            self.__primers[forward][part] = primer

        return self.__primers[forward][part]

    def __get_subseq(self, part_id, mlt_temp, forward):
        '''Get subsequence by melting temperature.'''
        seq = self.__get_seq(part_id)
        return seq_utils.get_seq_by_melt_temp(seq, mlt_temp, forward)[0]

    def __get_seq(self, ice_id):
        '''Get seq.'''
        if ice_id not in self.__seqs:
            self.__seqs[ice_id] = \
                self.__ice_client.get_ice_entry(ice_id).get_seq()

        return self.__seqs[ice_id]

    def __get_next_overhang(self):
        '''Get next overhang.'''
        ovrhng = self.__overhangs[self.__overhang_idx]
        self.__overhang_idx += 1
        return ovrhng.lower()

    def __get_domino(self, pair):
        '''Get domino.'''
        part1 = self.__get_domino_part(pair[0], True)
        part2 = self.__get_domino_part(pair[1], False)

        return part1 + part2

    def __get_domino_part(self, part, left):
        '''Get domino part from ICE id.'''
        primer = None

        if part not in self.__domino_parts[left]:
            if not left and part[0] == 'H':
                seq = self.__part_primers[part][0]
                return seq_utils.get_seq_by_melt_temp(seq,
                                                      self.__lcr_melt_temp,
                                                      True)[0]
            if left and part[2] == 'L':
                seq = self.__part_primers[part][1]
                return seq_utils.get_seq_by_melt_temp(seq,
                                                      self.__lcr_melt_temp,
                                                      False)[0]

            # else:
            primer = \
                self.__get_subseq(part[1], self.__lcr_melt_temp, not left)

            self.__domino_parts[left][part] = primer

        return self.__domino_parts[left][part]


def main(args):
    '''main method.'''
    designer = Lcr3Designer(args[0],
                            {'url': args[1],
                             'username': args[2],
                             'password': args[3]})

    design_parts = designer.get_design_parts()
    part_primers = designer.get_part_primers()
    pair_dominoes = designer.get_pair_dominoes()
    designer.close()

    for design, prts in design_parts.items():
        print(design, prts)

    print()

    for part, primers in part_primers.items():
        print(part, primers)

    print()

    for pair, domino in pair_dominoes.items():
        print(pair, domino)


if __name__ == '__main__':
    main(sys.argv[1:])
