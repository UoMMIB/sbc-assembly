'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import os
import shutil

from assembly import plate, worklist
from assembly.optimiser import score
import pandas as pd


def get_input_plates(dir_name):
    '''Get input plates.'''
    input_plates = {}

    for(dirpath, _, filenames) in os.walk(dir_name):
        for filename in filenames:
            if filename[-4:] == '.csv':
                df = pd.read_csv(os.path.join(dirpath, filename))
                _, name = os.path.split(filename)

                if 'well' in df.columns.values:
                    plt = plate.from_table(df, name)

                else:
                    plt = plate.from_plate(df, name)

                input_plates[plt.get_name()] = plt

    return input_plates


def run(wrtrs, sort_src, input_plates=None, plate_names=None,
        parent_out_dir_name='.'):
    '''Run pipeline.'''
    if not plate_names:
        plate_names = {}

    parent_out_dir = os.path.abspath(parent_out_dir_name)

    if os.path.exists(parent_out_dir):
        shutil.rmtree(parent_out_dir)

    for idx, writers in enumerate(wrtrs):
        if isinstance(writers, list):
            for wrt_idx, writer in enumerate(writers):
                input_plates.update(_run_writer(writer,
                                                str(idx + 1) + '_' +
                                                str(wrt_idx + 1),
                                                sort_src,
                                                input_plates,
                                                plate_names,
                                                parent_out_dir))
        else:
            input_plates.update(_run_writer(writers,
                                            str(idx + 1),
                                            sort_src,
                                            input_plates,
                                            plate_names,
                                            parent_out_dir))


def _run_writer(writer, name, sort_src, input_plates, plate_names,
                parent_out_dir):
    '''Run a writer.'''
    out_dir = os.path.join(parent_out_dir, name)
    os.makedirs(out_dir)

    worklist_gen = worklist.WorklistGenerator(writer.get_graph())
    plate_names['output'] = writer.get_output_name()
    wrklsts, plates = worklist_gen.get_worklist(sort_src,
                                                input_plates, plate_names)

    for plt in plates.values():
        plt.to_csv(out_dir)

    for wrklst in wrklsts:
        print(wrklst.name + '\t' + str(score(wrklst)))
        worklist.to_csv(wrklst, out_dir)

    return plates
