'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
import sys

from igraph import Graph

import matplotlib.pyplot as plt


def plot_graph(labels, tree, markersize=24, root=None):
    '''Plot labelled graph.'''
    positions = _get_positions(tree, root)

    # Plot edges:
    for edge in [e.tuple for e in tree.es]:
        x = [positions[edge[0]][0], positions[edge[1]][0]]
        y = [positions[edge[0]][1], positions[edge[1]][1]]
        plt.plot(x, y, lw=1, color='gray')
        plt.arrow(x[0], y[0], (x[1] - x[0]) / 2.0, (y[1] - y[0]) / 2.0,
                  head_width=0.1,
                  head_length=0.1,
                  fc='grey',
                  ec='grey')

    # Plot nodes:
    xs, ys = zip(*positions.values())

    plt.plot(xs, ys,
             'o',
             markersize=markersize,
             markerfacecolor='lightblue',
             markeredgecolor='grey')

    _annotate(xs, ys, labels)

    plt.axis('off')
    plt.show()


def plot_matrix(df):
    '''Plots tree.'''
    graph = Graph()

    roots = sorted(list(set(list(df.columns.values)) -
                        set(df.index.values)))

    indices = list(df.index.values)
    vertices = sorted(list(roots) + indices)

    for vertex in vertices:
        graph.add_vertex(vertex)

    for col in df.columns:
        for idx, coeff in enumerate(df[col]):
            if coeff > 0:
                print indices[idx] + ' -> ' + col + '\t\t' + \
                    str(vertices.index(indices[idx])) + ' -> ' + \
                    str(vertices.index(col))

                graph.add_edge(vertices.index(indices[idx]),
                               vertices.index(col))

                print ' '.join([str(e.tuple) for e in graph.es])

    plot_graph(vertices, graph,
               root=[vertices.index(root) for root in roots])


def _get_positions(tree, root):
    '''Gets positions.'''
    if root is None:
        root = [0]

    layout = tree.layout_reingold_tilford(mode="in", root=root)
    return {k: layout[k] for k in range(len(layout.coords))}


def _annotate(xs, ys, labels):
    '''Annotate.'''
    # TODO: Calculate accurately, based on text size:
    y_offset = 0.06
    x_offsets = [0.05 * len(val) for val in labels]

    for x, y, label, text_offset in zip(xs, ys, labels, x_offsets):
        plt.annotate(label, xy=(x - text_offset, y - y_offset))


def _get_graph(vertices=16, children=2):
    '''Gets graph.'''
    labels = map(str, range(vertices))
    graph = Graph.Tree(vertices, children)
    return labels, graph


def main(args):
    '''main method.'''
    labels, graph = _get_graph(int(args[0]), int(args[1]))
    plot_graph(labels, graph)


if __name__ == '__main__':
    main(sys.argv[1:])
