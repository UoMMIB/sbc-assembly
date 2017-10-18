'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
import sys

from igraph import Graph

import matplotlib.pyplot as plt


def plot_graph(labels, tree, root=None, outfile=None, layout_name='kk'):
    '''Plot labelled graph.'''
    positions = _get_positions(tree, root, layout_name)
    xs, ys = zip(*positions.values())
    ax = plt.gca()
    ax.set_xlim(min(xs), max(xs))
    ax.set_ylim(min(ys), max(ys))

    # Plot nodes:
    patches = _plot_vertices(positions, labels)

    # Plot edges:
    _plot_edges(positions, [e.tuple for e in tree.es], patches)

    plt.axis('off')

    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()


def plot_matrix(df, outfile=None, layout_name='kk'):
    '''Plots tree.'''
    graph = Graph(directed=True)

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

    plot_graph(vertices, graph,
               root=[vertices.index(root) for root in roots],
               outfile=outfile,
               layout_name=layout_name)


def _get_positions(tree, root, layout_name):
    '''Gets positions.'''
    if layout_name == 'tree':
        if root is None:
            root = [0]

        layout = tree.layout(layout_name, mode='in', root=root)
    else:
        layout = tree.layout(layout_name)

    return {k: layout[k] for k in range(len(layout.coords))}


def _plot_vertices(positions, labels):
    '''Plot vertices.'''
    patches = []

    xs, ys = zip(*positions.values())

    for x, y, label in zip(xs, ys, labels):
        bbox_props = dict(boxstyle='circle,pad=0.5',
                          fc='lightblue',
                          ec='grey',
                          lw=1)

        patches.append(plt.text(x, y, label, ha='center', va='center',
                                size=10,
                                zorder=-1,
                                bbox=bbox_props))
    return patches


def _plot_edges(positions, edges, patches):
    '''Plot edges.'''
    for edge in edges:
        x = [positions[edge[1]][0], positions[edge[0]][0]]
        y = [positions[edge[1]][1], positions[edge[0]][1]]

        plt.annotate('',
                     xy=(x[0], y[0]), xycoords='data',
                     xytext=(x[1], y[1]), textcoords='data',
                     zorder=1,
                     arrowprops=dict(arrowstyle='->',
                                     color='0.5',
                                     patchA=patches[edge[0]],
                                     patchB=patches[edge[1]],
                                     ),
                     )


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
