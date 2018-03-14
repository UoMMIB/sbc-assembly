'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import os
import shutil
import sys

from assembly import plate, utils, worklist
from assembly.app import part_pcr, part_qc, part_dig


def run(writers, input_plates=None, parent_out_dir_name='.'):
    '''Run pipeline.'''
    parent_out_dir = os.path.abspath(parent_out_dir_name)

    if os.path.exists(parent_out_dir):
        shutil.rmtree(parent_out_dir)

    for idx, writer in enumerate(writers):
        out_dir = os.path.join(parent_out_dir, str(idx + 1))
        os.makedirs(out_dir)

        worklist_gen = worklist.WorklistGenerator(writer.get_graph())
        wrklst, plates = worklist_gen.get_worklist(input_plates)

        for plt in plates:
            plt.to_csv(out_dir)

        worklist.to_csv(wrklst, out_dir)


def main(args):
    '''main method.'''
    ice_helper = utils.ICEHelper(args[0], args[1], args[2])
    parts_ice = ice_helper.get_parts(args[5:])
    part_ids = parts_ice.keys()

    writers = [part_pcr.PartPcrWriter(parts_ice, ice_helper),
               part_dig.PartDigestWriter(part_ids),
               part_qc.PartQcWriter(part_ids)]

    input_plates = {}

    for(dirpath, _, filenames) in os.walk(args[3]):
        for filename in filenames:
            if filename[-4:] == '.csv':
                plt = plate.from_table(os.path.join(dirpath, filename))
                input_plates[plt.get_name()] = plt

    run(writers, input_plates, parent_out_dir_name=args[4])


if __name__ == '__main__':
    main(sys.argv[1:])
