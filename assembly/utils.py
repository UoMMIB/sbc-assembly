'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
from igraph import Graph


def get_graph(df):
    '''Convert a Dataframe (matrix) to a graph.'''
    graph = Graph(directed=True)

    df = drop(df)

    roots = sorted(list(set(list(df.columns.values)) -
                        set(df.index.values)))

    indices = list(df.index.values)
    vertices = sorted(list(roots) + indices)

    for vertex in vertices:
        graph.add_vertex(vertex)

    for col in df.columns:
        for idx, coeff in enumerate(df[col]):
            if coeff > 0:
                graph.add_edge(vertices.index(indices[idx]),
                               vertices.index(col))

    return graph, roots, vertices


def drop(df):
    '''Drop empty columns and rows.'''
    df = df[df.columns[(df != 0).any()]]
    return df[(df.T != 0).any()]
