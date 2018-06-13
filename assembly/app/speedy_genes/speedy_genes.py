'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=unsubscriptable-object
import itertools
import os
import sys

from synbiochem import utils

from assembly import pipeline, worklist
from assembly.graph_writer import GraphWriter
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


class SpeedyGenesWriter(GraphWriter):
    '''Class for generating Part digest worklist graphs.'''

    def __init__(self,
                 input_plates,
                 n_mutated=0,
                 n_blocks=1,
                 output_name='output',
                 graph_filename=None):
        self.__plates = []
        self.__oligos, self.__mutant_oligos = \
            self.__read_plates(input_plates)
        self.__n_mutated = n_mutated
        self.__n_blocks = n_blocks
        self.__graph_filename = graph_filename
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        designs = self.__combine()
        ingredients = _get_ingredients(designs)
        optim = Optimiser(ingredients)
        self.__form_graph(optim.get_matrix(), optim.get_reagents())

        if self.__graph_filename:
            self.plot_graph(outfile=self.__graph_filename)

    def __read_plates(self, input_plates):
        '''Read plates.'''
        oligos = utils.sort([obj['id']
                             for obj in input_plates['wt'].get_all().values()])
        mutant_oligos = ((oligo, oligo + 'm') for oligo in oligos)
        return oligos, mutant_oligos

    def __combine(self):
        '''Design combinatorial assembly.'''

        # Assertion sanity checks:
        assert len(self.__oligos) % 2 == 0
        assert len(self.__oligos) / self.__n_blocks >= 2
        assert self.__mutant_oligos if self.__n_mutated > 0 else True

        designs = []

        # Get combinations:
        combis = itertools.combinations(self.__mutant_oligos,
                                        self.__n_mutated)

        for combi in combis:
            design = list(self.__oligos)

            for var in combi:
                design[design.index(var[0])] = var[1]

            block_lengths = [0] * self.__n_blocks

            for idx in itertools.cycle(range(0, self.__n_blocks)):
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

    def __form_graph(self, df, reagents):
        '''Convert a Dataframe (matrix) to a graph.'''
        df = _drop(df)

        roots = sorted(list(set(list(df.columns.values)) -
                            set(df.index.values)))

        indices = list(df.index.values)
        vertix_names = sorted(list(roots) + indices)
        vertices = {vertix_name:
                    self._add_vertex(vertix_name,
                                     {'is_reagent': vertix_name in reagents})
                    for vertix_name in vertix_names}

        for col in df.columns:
            for idx, coeff in enumerate(df[col]):
                if coeff > 0:
                    self._add_edge(vertices[indices[idx]],
                                   vertices[col],
                                   {'Volume': coeff})


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


def _get_prepooled_oligo(oligo_id, wt=True):
    '''Get pre-pooled oligo.'''
    all_ingredients = []

    if wt:
        all_ingredients = ((oligo_id, 10, False), ('h2o', 190, True))

    return all_ingredients


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
                 [('h2o', h2o_vol, True)])


def _get_gene_ingredients(design, des_vols):
    '''Gets sub ingredients.'''
    vols = [des_vols['inner']] * len(design)
    vols[0] = des_vols['primer']
    vols[-1] = des_vols['primer']
    mm_vol = 50.0 - sum(vols)

    return tuple([('mm', mm_vol, True)] +
                 list(zip(design, vols, [False] * len(design))))


def _drop(df):
    '''Drop empty columns and rows.'''
    df = df[df.columns[(df != 0).any()]]
    return df[(df.T != 0).any()]


def main(args):
    '''main method.'''
    # oligos = [str(val + 1) for val in range(0, int(args[0]))]
    # mutant_oligos = ((oligo, oligo + 'm') for oligo in oligos)
    input_plates = pipeline.get_input_plates(args[0])

    writers = [SpeedyGenesWriter(input_plates,
                                 int(args[1]),
                                 int(args[2]))]

    out_dir_name = os.path.join(args[3], 'speedy_genes')
    pipeline.run(writers, input_plates, {}, out_dir_name)

    worklist.format_worklist(out_dir_name)


if __name__ == '__main__':
    main(sys.argv[1:])
