'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys

from igraph import Graph

from assembly.worklist import WorklistGenerator
from synbiochem.utils.graph_utils import add_edge, add_vertex


def get_graph(plasmid_ids):
    '''Get graph.'''
    graph = Graph(directed=True)

    for plasmid_id in plasmid_ids:
        part = add_vertex(graph, plasmid_id + '_part', {'is_reagent': False})
        primer_mix = add_vertex(graph, 'mm', {'is_reagent': True})

        add_edge(graph, primer_mix, part, {'Volume': 24.0})

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
