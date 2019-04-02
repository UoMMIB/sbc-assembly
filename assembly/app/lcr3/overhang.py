'''
SequenceGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=superfluous-parens
import os.path
import sys

from synbiochem.utils import seq_utils


def get_seqs(num_overhangs=128, target_melt_temp=70.0, max_repeat_nuc=3,
             evalue=1e-3):
    '''Get overhangs.'''
    overhangs = {}

    directory = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(directory,
                            '%i_%.3f_%i_%.3e.txt' % (num_overhangs,
                                                     target_melt_temp,
                                                     max_repeat_nuc,
                                                     evalue))

    if os.path.exists(filename):
        with open(filename) as fle:
            overhangs = {idx: line.strip() for idx, line in enumerate(fle)}

    while len(overhangs) < num_overhangs:
        overhang = seq_utils.get_rand_seq_by_melt_temp(target_melt_temp,
                                                       max_repeat_nuc)[0]

        if overhangs and not _do_blast(overhangs, {'query': overhang}, evalue):
            continue

        overhangs[str(len(overhangs))] = overhang

    overhangs = list(overhangs.values())

    with open(filename, 'w') as fle:
        for overhang in overhangs:
            fle.write(overhang + '\n')

    return overhangs[:num_overhangs]


def _get_seqs():
    '''Get seqs.'''


def _do_blast(subjects, queries, evalue):
    '''Runs BLAST, filtering results.'''
    for result in seq_utils.do_blast(subjects, queries, evalue=evalue,
                                     word_size=4):
        if result.alignments:
            return False

    return True


def main(args):
    '''main method.'''
    get_seqs(int(args[0]), float(args[1]), int(args[2]), float(args[3]))


if __name__ == '__main__':
    main(sys.argv[1:])
