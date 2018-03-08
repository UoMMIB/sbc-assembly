'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys

from igraph import Graph

from assembly.worklist import WorklistGenerator


_REAGENTS = {'water': 23.0, 'mm': 25.0}


def get_graph(plasmid_ids):
    '''Get graph.'''
    graph = Graph(directed=True)

    reagents = {add_vertex(graph, reagent, {'is_reagent': True}): vol
                for reagent, vol in _REAGENTS.iteritems()}

    for plasmid_id in plasmid_ids:
        plasmid = add_vertex(graph, plasmid_id, {'is_reagent': False})
        primer_mix = add_vertex(graph, _get_primer_mix_id(plasmid_id),
                                {'is_reagent': False})
        part = add_vertex(graph, plasmid_id + '_part', {'is_reagent': False})

        for reagent, vol in reagents.iteritems():
            add_edge(graph, reagent, part, vol)

        add_edge(graph, plasmid, part, 1.0)
        add_edge(graph, primer_mix, part, 1.0)

    return graph


def add_vertex(graph, name, kwds=None):
    '''Add vertex.'''
    try:
        return graph.vs.find(name)
    except ValueError:
        if not kwds:
            kwds = {}

        graph.add_vertex(name, **kwds)
        return graph.vs.find(name)


def add_edge(graph, vertex_from, vertex_to, vol):
    '''Add edge.'''
    graph.add_edge(vertex_from.index, vertex_to.index)
    graph.es[graph.ecount() - 1]['vol'] = vol


def _get_primer_mix_id(plasmid_id):
    '''Get primer mix id.'''
    return 'primer_mix'


def main(args):
    '''main method.'''
    graph = get_graph(args)

    from assembly.graph_plotter import plot_graph
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