'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys

from igraph import Graph

from assembly import worklist
from synbiochem.utils.graph_utils import add_edge, add_vertex


def get_graph(part_ids):
    '''Get graph.'''
    graph = Graph(directed=True)

    ladder = add_vertex(graph, 'ladder', {'is_reagent': True, 'well': 'H12'})
    bffer = add_vertex(graph, 'buffer', {'is_reagent': True})
    ladder_product = add_vertex(graph, 'ladder_product',
                                {'is_reagent': False, 'well': 'H12'})
    add_edge(graph, ladder, ladder_product, {'Volume': 2.0})
    add_edge(graph, bffer, ladder_product, {'Volume': 22.0})

    for part_id in part_ids:
        part = add_vertex(graph, part_id, {'is_reagent': False})
        product = add_vertex(graph, part_id + '_product',
                             {'is_reagent': False})

        add_edge(graph, part, product, {'Volume': 1.0})
        add_edge(graph, bffer, product, {'Volume': 23.0})

    return graph


def main(args):
    '''main method.'''
    graph = get_graph(args)

    worklist_gen = worklist.WorklistGenerator(graph)
    wrklst, plates = worklist_gen.get_worklist()

    for plt in plates:
        plt.to_csv()

    worklist.to_csv(wrklst)


if __name__ == '__main__':
    main(sys.argv[1:])
