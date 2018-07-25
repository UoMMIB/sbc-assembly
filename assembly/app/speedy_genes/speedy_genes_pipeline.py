'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
from collections import defaultdict
import itertools
import os
import sys
from time import gmtime, strftime

from synbiochem import utils

from assembly import pipeline, worklist
from assembly.app.speedy_genes.block import InnerBlockPoolWriter, \
    BlockPcrWriter, BlockPoolWriter
from assembly.app.speedy_genes.dilution import WtOligoDilutionWriter
from assembly.app.speedy_genes.gene import CombiGenePcrWriter
from assembly.app.speedy_genes.pool import MutOligoPoolWriter


def run(plate_dir, max_mutated, n_blocks, out_dir_parent, exp_name):
    '''run method.'''
    assert len(exp_name) < 6

    dte = strftime("%y%m%d", gmtime())

    input_plates = pipeline.get_input_plates(plate_dir)
    oligos, mutant_oligos, primers = _read_plates(input_plates)
    designs = _combine(oligos, mutant_oligos, max_mutated, n_blocks)

    writers = [
        WtOligoDilutionWriter(oligos + primers, designs, 20, 10, 200,
                              exp_name + '-wt-dil'),
        MutOligoPoolWriter(mutant_oligos, 10, exp_name + '-mut-pl'),
        InnerBlockPoolWriter(designs, 5, exp_name + '-templ'),
        BlockPcrWriter(designs, 1.2, 1.5, 3, 22.8, exp_name + '-pcr1'),
        BlockPoolWriter(designs, 4.5, exp_name + '-blcks'),
        CombiGenePcrWriter(designs, 4, 1.5, 1.5, 3, 14.5,
                           ['5-primer_dil', '28'], exp_name + '-pcr2')
    ]

    out_dir_name = os.path.join(out_dir_parent, dte + exp_name)

    pipeline.run(writers, True, input_plates,
                 parent_out_dir_name=out_dir_name)

    worklist.format_worklist(out_dir_name)


def _read_plates(input_plates):
    '''Read plates.'''
    oligos = utils.sort(
        [obj['id'] for obj in input_plates['wt'].get_all().values()
         if obj['id'].isdigit()])

    primers = [obj['id'] for obj in input_plates['wt'].get_all().values()
               if not obj['id'].isdigit()]

    mutant_oligos = defaultdict(list)

    for obj in input_plates['mut'].get_all().values():
        mutant_oligos[obj['parent']].append(obj['id'])

    return oligos, mutant_oligos, primers


def _combine(oligos, mutant_oligos, max_mutated, n_blocks):
    '''Design combinatorial assembly.'''

    # Assertion sanity checks:
    assert len(oligos) % 2 == 0
    assert len(oligos) / n_blocks >= 2
    assert mutant_oligos if max_mutated > 0 else True

    designs = []

    # Get combinations:
    for n_mutated in range(max_mutated + 1):
        designs.extend(_get_combis(oligos, mutant_oligos, n_mutated, n_blocks))

    return designs


def _get_combis(oligos, mutant_oligos, n_mutated, n_blocks):
    '''Get combinations.'''
    designs = []

    for combi in itertools.combinations(list(mutant_oligos), n_mutated):
        design = list(oligos)

        for wt_id in combi:
            design[design.index(wt_id)] = wt_id + 'm'

        block_lengths = [0] * n_blocks

        for idx in itertools.cycle(range(0, n_blocks)):
            block_lengths[idx] = block_lengths[idx] + 2

            if sum(block_lengths) == len(design):
                break

        idx = 0
        blocks = []

        for val in block_lengths:
            blocks.append(design[idx: idx + val])
            idx = idx + val

        designs.append(blocks)

    return designs


def main(args):
    '''main method.'''
    import cProfile

    pr = cProfile.Profile()
    pr.enable()

    run(args[0], int(args[1]), int(args[2]), args[3], args[4])

    pr.disable()

    pr.print_stats(sort='cumtime')


if __name__ == '__main__':
    main(sys.argv[1:])
