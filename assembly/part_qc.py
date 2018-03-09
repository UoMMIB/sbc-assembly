'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys

from igraph import Graph

from assembly.worklist import WorklistGenerator
from synbiochem.utils.graph_utils import add_edge, add_vertex


def get_graph(part_ids):
    '''Get graph.'''
    graph = Graph(directed=True)

    ladder = add_vertex(graph, 'ladder', {'is_reagent': False})
    bffer = add_vertex(graph, 'buffer', {'is_reagent': True, 'well': 'H12'})
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

    from synbiochem.utils.graph_utils import plot_graph
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
