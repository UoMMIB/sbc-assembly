'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys

from assembly import utils
from assembly.app import part_pcr, part_qc, part_dig


def main(args):
    '''main method.'''
    ice_helper = utils.ICEHelper(args[0], args[1], args[2])
    parts_ice = ice_helper.get_parts(args[3:])
    part_ids = [part_ice['id'] for part_ice in parts_ice]

    classes = [part_pcr.PartPcrWriter(parts_ice, ice_helper),
               part_dig.PartDigestWriter(part_ids),
               part_qc.PartQcWriter(part_ids)]


if __name__ == '__main__':
    main(sys.argv[1:])
