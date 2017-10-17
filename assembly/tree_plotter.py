'''
AssemblyGenie (c) GeneGenie 2017

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
import sys

from igraph import Graph
import matplotlib.pyplot as plt


def plot(labels, tree):
    '''Plot labelled tree.'''
    lay = tree.layout('tree', 0)
    position = {k: lay[k] for k in range(len(lay.coords))}

    _, ax = plt.subplots()
    ax.axis('off')

    for edge in [e.tuple for e in tree.es]:
        x = [position[edge[0]][0], position[edge[1]][0]]
        y = [position[edge[0]][1], position[edge[1]][1]]
        plt.plot(x, y, lw=1, color='gray')

    xs, ys = zip(*position.values())
    ax.plot(xs, ys, 'o')

    for x, y, label in zip(xs, ys, labels):
        ax.annotate(label, xy=(x, y))

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
