'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=unsubscriptable-object
import itertools
import sys

from igraph import Graph

from assembly import worklist
from assembly.optimiser import Optimiser


_DEFAULT_OLIGO_VOLS = {
    'block': {
        'primer': 3.0,
        'oligo_pool': 0.75
    },
    'gene': {
        'primer': 3.0,
        'inner': 0.75
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


def _get_ingredients(designs, oligo_vols=None):
    '''Gets ingredients.'''
    all_ingredients = []

    if not oligo_vols:
        oligo_vols = _DEFAULT_OLIGO_VOLS

    max_block_size = max([len(design) for design in designs[0]])

    for design in designs:
        ingredients = [_get_block_ingredients(block,
                                              oligo_vols['block'],
                                              max_block_size)
                       for block in design]

        ingredients = [design[0][0]] + ingredients + [design[-1][-1]]

        all_ingredients.append((_get_gene_ingredients(ingredients,
                                                      oligo_vols['gene']),
                                0.0, False))

    return tuple((all_ingredients, 0.0, False))


def _get_block_ingredients(design, des_vols, max_block_size):
    '''Gets sub ingredients.'''
    vols = [des_vols['primer'], des_vols['oligo_pool'], des_vols['primer']]
    mm_vol = 50.0 - sum(vols)

    components = [design[0],
                  _get_oligo_pool(design, max_block_size),
                  design[-1]]

    return tuple([('mm', mm_vol, True)] +
                 list(zip(components, vols, [False] * len(components))))


def _get_oligo_pool(design, max_block_size, oligo_pool_vol=10.0):
    '''Get oligo pool.'''
    h2o_vol = (max_block_size - len(design)) * oligo_pool_vol
    return tuple([(oligo, oligo_pool_vol, False) for oligo in design[1:-1]] +
                 [('h2o', h2o_vol, False)])


def _get_gene_ingredients(design, des_vols):
    '''Gets sub ingredients.'''
    vols = [des_vols['inner']] * len(design)
    vols[0] = des_vols['primer']
    vols[-1] = des_vols['primer']
    mm_vol = 50.0 - sum(vols)

    return tuple([('mm', mm_vol, True)] +
                 list(zip(design, vols, [False] * len(design))))


def _get_graph(df, reagents):
    '''Convert a Dataframe (matrix) to a graph.'''
    graph = Graph(directed=True)

    df = _drop(df)

    roots = sorted(list(set(list(df.columns.values)) -
                        set(df.index.values)))

    indices = list(df.index.values)
    vertices = sorted(list(roots) + indices)

    for vertex in vertices:
        graph.add_vertex(vertex)
        graph.vs[graph.vcount() - 1]['is_reagent'] = vertex in reagents

    for col in df.columns:
        for idx, coeff in enumerate(df[col]):
            if coeff > 0:
                graph.add_edge(vertices.index(indices[idx]),
                               vertices.index(col))
                graph.es[graph.ecount() - 1]['Volume'] = coeff

    return graph


def _drop(df):
    '''Drop empty columns and rows.'''
    df = df[df.columns[(df != 0).any()]]
    return df[(df.T != 0).any()]


def _test(n_oligos, n_mutated, n_blocks):
    '''Test method.'''
    oligos = [str(val + 1) for val in range(0, n_oligos)]
    mutant_oligos = ((oligo, oligo + 'm') for oligo in oligos)
    return combine(oligos, n_mutated, mutant_oligos, n_blocks)


def main(args):
    '''main method.'''
    ingredients = _test(int(args[0]), int(args[1]), int(args[2]))

    # Convert ingredients to graph:
    optim = Optimiser(ingredients)
    graph = _get_graph(optim.get_matrix(), optim.get_reagents())

    worklist_gen = worklist.WorklistGenerator(graph)
    wrklst, plates = worklist_gen.get_worklist(args[4]
                                               if len(args) > 4 else None)

    out_dir = args[3]

    for plt in plates.values():
        plt.to_csv(out_dir)

    worklist.to_csv(wrklst, out_dir)
    worklist.format_worklist(out_dir)


if __name__ == '__main__':
    main(sys.argv[1:])
