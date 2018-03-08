'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import itertools
import sys

from assembly.optimiser import Optimiser
from assembly.utils import get_graph
from assembly.worklist import WorklistGenerator


_DEFAULT_OLIGO_VOLS = {
    'block': {
        'primer': 3.0,
        'oligo_pool': 0.75
    },
    'gene': {
        'primer': 3,
        'inner': 0.75
    }}

_DEFAULT_REAG_VOLS = {
    'block': {
        'mm': 50.0
    },
    'gene': {
        'mm': 45.0
    }}


def combine(oligos, n_mutated=0, mutant_oligos=None, n_blocks=1):
    '''Design combinatorial assembly.'''
    designs = _combine(oligos, n_mutated, mutant_oligos, n_blocks)
    return _get_ingredients(designs)


def _combine(oligos, n_mutated, mutant_oligos, n_blocks):
    '''Design combinatorial assembly.'''

    # Assertion sanity checks:
    assert len(oligos) % 2 == 0
    assert len(oligos) / n_blocks >= 2
    assert mutant_oligos if n_mutated > 0 else True

    designs = []

    # Get combinations:
    combis = itertools.combinations(mutant_oligos, n_mutated)

    for combi in combis:
        design = list(oligos)

        for var in combi:
            design[design.index(var[0])] = var[1]

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


def _get_ingredients(designs, oligo_vols=None, reagent_vols=None):
    '''Gets ingredients.'''
    all_ingredients = []

    if not oligo_vols:
        oligo_vols = _DEFAULT_OLIGO_VOLS

    if not reagent_vols:
        reagent_vols = _DEFAULT_REAG_VOLS

    for design in designs:
        ingredients = [_get_block_ingredients(block,
                                              oligo_vols['block'],
                                              reagent_vols['block'])
                       for block in design]

        ingredients = [design[0][0]] + ingredients + [design[-1][-1]]

        all_ingredients.append((_get_gene_ingredients(ingredients,
                                                      oligo_vols['gene'],
                                                      reagent_vols['gene']),
                                0.0, False))

    return tuple((all_ingredients, 0.0, False))


def _get_block_ingredients(design, des_vols, reagents):
    '''Gets sub ingredients.'''
    vols = [des_vols['primer'], des_vols['oligo_pool'], des_vols['primer']]
    components = [design[0], _get_oligo_pool(design), design[-1]]
    return tuple([(reag, vol, True)
                  for reag, vol in reagents.iteritems()] +
                 zip(components, vols, [False] * len(components)))


def _get_oligo_pool(design, oligo_pool_vol=10.0):
    '''Get oligo pool.'''
    return tuple([(oligo, oligo_pool_vol, False) for oligo in design[1:-1]])


def _get_gene_ingredients(design, des_vols, reagents):
    '''Gets sub ingredients.'''
    vols = [des_vols['inner']] * len(design)
    vols[0] = des_vols['primer']
    vols[-1] = des_vols['primer']
    return tuple([(reag, vol, True)
                  for reag, vol in reagents.iteritems()] +
                 zip(design, vols, [False] * len(design)))


def _test(n_mutated, n_blocks):
    '''Test method.'''
    oligos = [str(val) for val in range(1, 29)]
    mutant_oligos = ((oligo, oligo + 'm') for oligo in oligos)
    return combine(oligos, n_mutated, mutant_oligos, n_blocks)


def main(args):
    '''main method.'''
    ingredients = _test(int(args[0]), int(args[1]))

    # Convert ingredients to graph:
    optim = Optimiser(ingredients)
    graph = get_graph(optim.get_matrix(), optim.get_reagents())

    from assembly.tree_plotter import plot_graph
    plot_graph(graph, layout_name='tree')

    worklist_gen = WorklistGenerator(graph)
    worklist, plates = worklist_gen.get_worklist()

    for plate_id in sorted(plates, reverse=True):
        print 'Plate: ' + str(plate_id)
        print plates[plate_id]
        print

    print worklist


if __name__ == '__main__':
    main(sys.argv[1:])
