'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
import sys


def assemble(recipes):
    '''Assembles a recipe.'''
    for recipe in recipes:
        _assemble(recipe)


def _assemble(recipe, level=0):
    '''Recursively assembles a recipe.'''
    print str(level) + '\t' + str(recipe)

    for term in recipe[0]:
        if isinstance(term, tuple):
            _assemble(term, level + 1)


def main(args):
    '''main method.'''
    a = (('A', 5), ('B', 7.5))
    b = (('A', 50), ('C', 17.5))
    c = (('A', 35), (b, 27.5))
    p = ((('X', 3), (a, 2), (c, 4)), 0)
    assemble([p, (c, 0)])


if __name__ == '__main__':
    main(sys.argv[1:])
