'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
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
        'mastermix': 50.0
    },
    'gene': {
        'mastermix': 45.0
    }}


def get_ingredients(designs, concs=None, reagents=None):
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

    from geneorator.combinatorial import combine
    designs = combine(oligos, int(args[0]), mutant_oligos, int(args[1]))

    for design in designs:
        print design

    ingredients = get_ingredients(designs)

    # for ingredient in ingredients[0]:
    #    print ingredient

    optim = Optimiser(ingredients)
    optim.plot('init.png')
    optim.save_matrix('init.csv')
    optim.optimise()
    optim.plot('optim.png')
    optim.save_matrix('optim.csv')


if __name__ == '__main__':
    main(sys.argv[1:])
