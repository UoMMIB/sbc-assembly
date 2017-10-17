'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
import sys

from igraph import Graph
import matplotlib.pyplot as plt


def plot(labels, tree, markersize=24):
    '''Plot labelled tree.'''
    lay = tree.layout('tree', 0)
    position = {k: lay[k] for k in range(len(lay.coords))}

    _, ax = plt.subplots()
    ax.axis('off')

    xs, ys = zip(*position.values())
    plt.plot(xs, ys,
             'o',
             markersize=markersize,
             markerfacecolor='lightblue',
             markeredgecolor='grey')

    for edge in [e.tuple for e in tree.es]:
        x = [position[edge[0]][0], position[edge[1]][0]]
        y = [position[edge[0]][1], position[edge[1]][1]]
        # plt.plot(x, y, lw=1, color='gray')
        plt.arrow(x[0], y[0], x[1] - x[0], y[1] - y[0],
                  head_width=0.05,
                  head_length=0.1,
                  fc='grey',
                  ec='grey')

    for x, y, label in zip(xs, ys, labels):
        ax.annotate(label, xy=(x - 0.075, y - 0.075))

    plt.show()


def _get_tree(vertices=16, children=2):
    '''Gets tree.'''
    labels = map(str, range(vertices))
    tree = Graph.Tree(vertices, children)
    return labels, tree


def main(args):
    '''main method.'''
    labels, tree = _get_tree(int(args[0]), int(args[1]))
    plot(labels, tree)


if __name__ == '__main__':
    main(sys.argv[1:])
