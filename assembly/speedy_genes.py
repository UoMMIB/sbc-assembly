'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
import sys

_DEFAULT_VOLS = {
    'block': {
        'outer': 500,
        'inner': 30
    },
    'gene': {
        'outer': 400,
        'inner': 25
    }}

_DEFAULT_REAG = {
    'block': {
        'mastermix': 50
    },
    'gene': {
        'mastermix': 45
    }}


def get_recipes(designs, vols=None, reagents=None):
    '''Gets recipes.'''
    recipes = []

    if not vols:
        vols = _DEFAULT_VOLS

    if not reagents:
        reagents = _DEFAULT_REAG

    for design in designs:
        recipe = [_get_sub_recipe(block, vols['block'], reagents['block'])
                  for block in design]

        recipes.append(recipe)

    return recipes


def _get_sub_recipe(design, des_vols, reagents):
    '''Gets sub recipe.'''
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

    for recipe in get_recipes(designs):
        print recipe


if __name__ == '__main__':
    main(sys.argv[1:])
