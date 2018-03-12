'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys
from assembly.app import part_pcr, part_qc, part_dig


def main(args):
    '''main method.'''
    modules = [part_pcr, part_qc, part_dig]


if __name__ == '__main__':
    main(sys.argv[1:])
