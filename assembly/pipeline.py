'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import os
import shutil

from assembly import worklist


def run(writers, input_plates=None, plate_names=None, parent_out_dir_name='.'):
    '''Run pipeline.'''
    parent_out_dir = os.path.abspath(parent_out_dir_name)

    if os.path.exists(parent_out_dir):
        shutil.rmtree(parent_out_dir)

    for idx, writers in enumerate(writers):
        if isinstance(writers, list):
            for wrt_idx, writer in enumerate(writers):
                _run_writer(writer, str(idx + 1) + '_' + str(wrt_idx + 1),
                            input_plates, plate_names, parent_out_dir)
        else:
            _run_writer(writers, str(idx + 1), input_plates, plate_names,
                        parent_out_dir)


def _run_writer(writer, name, input_plates, plate_names, parent_out_dir):
    '''Run a writer.'''
    out_dir = os.path.join(parent_out_dir, name)
    os.makedirs(out_dir)

    worklist_gen = worklist.WorklistGenerator(writer.get_graph())
    wrklst, plates = worklist_gen.get_worklist(input_plates, plate_names)

    for plt in plates:
        plt.to_csv(out_dir)

    worklist.to_csv(wrklst, out_dir)
