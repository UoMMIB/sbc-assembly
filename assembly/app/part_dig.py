'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys

from igraph import Graph

from assembly import worklist
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

    worklist_gen = worklist.WorklistGenerator(graph)
    wrklst, plates = worklist_gen.get_worklist()

    for plt in plates:
        plt.to_csv()

    worklist.to_csv(wrklst)


if __name__ == '__main__':
    main(sys.argv[1:])
