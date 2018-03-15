'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import os
import shutil

from assembly import worklist


def run(writers, reagent_plate_name, input_plates=None,
        parent_out_dir_name='.'):
    '''Run pipeline.'''
    parent_out_dir = os.path.abspath(parent_out_dir_name)

    if os.path.exists(parent_out_dir):
        shutil.rmtree(parent_out_dir)

    for idx, writer in enumerate(writers):
        out_dir = os.path.join(parent_out_dir, str(idx + 1))
        os.makedirs(out_dir)

        worklist_gen = worklist.WorklistGenerator(writer.get_graph())
        wrklst, plates = worklist_gen.get_worklist(reagent_plate_name,
                                                   input_plates)

        for plt in plates:
            plt.to_csv(out_dir)

        worklist.to_csv(wrklst, out_dir)
