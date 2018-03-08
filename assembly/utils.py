'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=unsubscriptable-object
from igraph import Graph
from scipy.spatial.distance import cityblock

from assembly import plate


def get_graph(df, reagents):
    '''Convert a Dataframe (matrix) to a graph.'''
    graph = Graph(directed=True)

    df = drop(df)

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
                graph.es[graph.ecount() - 1]['coeff'] = coeff

    return graph


def get_roots(graph):
    '''Get roots.'''
    return [vs for vs, outdg in zip(graph.vs, graph.outdegree())
            if not outdg]


def drop(df):
    '''Drop empty columns and rows.'''
    df = df[df.columns[(df != 0).any()]]
    return df[(df.T != 0).any()]


def get_optimal_src_dest(srcs, dests):
    '''Get the optimial src and dest pair for efficient pipetting.'''
    shortest_dist = float('inf')
    optimal_pair = None

    for src_plate, src_wells in srcs.iteritems():
        for dest_plate, dest_wells in dests.iteritems():
            for src_well in src_wells:
                for dest_well in dest_wells:
                    dist = cityblock(plate.get_indices(src_well),
                                     plate.get_indices(dest_well))

                    if dist < shortest_dist:
                        shortest_dist = dist
                        optimal_pair = [src_plate, src_well,
                                        dest_plate, dest_well]
    return optimal_pair
