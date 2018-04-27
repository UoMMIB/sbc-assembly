'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import os
import shutil

from assembly import worklist


def run(wrtrs, input_plates=None, plate_names=None, parent_out_dir_name='.'):
    '''Run pipeline.'''
    parent_out_dir = os.path.abspath(parent_out_dir_name)

    if os.path.exists(parent_out_dir):
        shutil.rmtree(parent_out_dir)

    for idx, writers in enumerate(wrtrs):
        if isinstance(writers, list):
            next_input_plates = [_run_writer(writer,
                                             str(idx + 1) + '_' +
                                             str(wrt_idx + 1),
                                             input_plates,
                                             plate_names,
                                             parent_out_dir)
                                 for wrt_idx, writer in enumerate(writers)]

            input_plates = [plate
                            for plates in next_input_plates
                            for plate in plates]
        else:
            input_plates = _run_writer(writers, str(idx + 1), input_plates,
                                       plate_names, parent_out_dir)


def _run_writer(writer, name, input_plates, plate_names, parent_out_dir):
    '''Run a writer.'''
    out_dir = os.path.join(parent_out_dir, name)
    os.makedirs(out_dir)

    worklist_gen = worklist.WorklistGenerator(writer.get_graph())
    plate_names['output'] = writer.get_output_name()
    wrklst, plates = worklist_gen.get_worklist(input_plates, plate_names)

    for plt in plates.values():
        plt.to_csv(out_dir)

    worklist.to_csv(wrklst, out_dir)

    return plates
