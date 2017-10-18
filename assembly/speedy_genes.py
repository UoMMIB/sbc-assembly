'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
import itertools
import sys

from assembly.optimiser import Optimiser


_DEFAULT_CONCS = {
    'block': {
        'outer': 500.0,
        'inner': 30.0
    },
    'gene': {
        'outer': 400.0,
        'inner': 25.0
    }}

_DEFAULT_REAG = {
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


def _get_ingredients(designs, concs=None, reagents=None):
    '''Gets ingredients.'''
    all_ingredients = []

    if not concs:
        concs = _DEFAULT_CONCS

    if not reagents:
        reagents = _DEFAULT_REAG

    for design in designs:
        ingredients = [_get_sub_ingredients(block, concs['block'],
                                            reagents['block'])
                       for block in design]

        ingredients = [design[0][0]] + ingredients + [design[-1][-1]]

        all_ingredients.append((_get_sub_ingredients(ingredients,
                                                     concs['gene'],
                                                     reagents['gene']),
                                0.0))

    return tuple((all_ingredients, 0.0))


def _get_sub_ingredients(design, des_vols, reagents):
    '''Gets sub ingredients.'''
    vols = [des_vols['inner']] * len(design)
    vols[0] = des_vols['outer']
    vols[-1] = des_vols['outer']
    return tuple(list(reagents.iteritems()) + zip(design, vols))


def main(args):
    '''main method.'''
    oligos = [str(val) for val in range(1, 29)]
    mutant_oligos = ((oligo, oligo + 'm') for oligo in oligos)

    ingredients = combine(oligos, int(args[0]), mutant_oligos, int(args[1]))

    optim = Optimiser(ingredients)
    optim.plot('init.png', layout_name='tree')
    optim.save_matrix('init.csv')
    optim.optimise()
    optim.plot('optim.png', layout_name='tree')
    optim.save_matrix('optim.csv')


if __name__ == '__main__':
    main(sys.argv[1:])
