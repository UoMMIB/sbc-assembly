'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
from igraph import Graph

from assembly.utils import get_graph
import matplotlib.pyplot as plt


def plot_graph(labels, tree, colours, root=None, outfile=None,
               layout_name='kk'):
    '''Plot labelled graph.'''
    positions = _get_positions(tree, root, layout_name)
    xs, ys = zip(*positions.values())
    ax = plt.gca()
    ax.set_xlim(min(xs), max(xs))
    ax.set_ylim(min(ys), max(ys))

    # Plot nodes:
    patches = _plot_vertices(positions, labels, colours)

    # Plot edges:
    _plot_edges(positions, [e.tuple for e in tree.es], patches)

    plt.axis('off')

    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()


def plot_matrix(df, reagents, outfile=None, layout_name='kk'):
    '''Plots tree.'''
    graph, roots, vertices = get_graph(df)
    colours = ['lightgreen' if reagents[vertex] else 'lightblue'
               for vertex in vertices]

    plot_graph(vertices, graph, colours,
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


def _plot_vertices(positions, labels, colours):
    '''Plot vertices.'''
    patches = []

    xs, ys = zip(*positions.values())

    for x, y, label, colour in zip(xs, ys, labels, colours):
        bbox_props = dict(boxstyle='circle,pad=0.5',
                          fc=colour,
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
