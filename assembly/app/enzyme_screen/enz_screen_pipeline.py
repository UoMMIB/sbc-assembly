'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
from collections import Counter
import os
import re
import sys
from time import gmtime, strftime

from assembly import pipeline, plate, worklist
from assembly.graph_writer import GraphWriter
import pandas as pd


class EnzymeScreenWriter(GraphWriter):
    '''Class for generating enzyme screen worklist graphs.'''

    def __init__(self, df, blank_ids, output_name='enz_scr', replicates=2):
        self.__df = df
        self.__blank_ids = blank_ids
        self.__replicates = replicates
        GraphWriter.__init__(self, output_name)

    def _initialise(self):
        assay_ids = []

        for _, row in self.__df.iterrows():
            for _ in range(self.__replicates):
                part_ids = re.split(r'\s\+\s',
                                    str(row['Part ID (s)']).strip())

                self.__add_assay(part_ids, row['Substrate'], assay_ids)

        for substrate in self.__df['Substrate'].unique():
            for _ in range(self.__replicates):
                for blank_id in self.__blank_ids:
                    self.__add_assay([blank_id], substrate, assay_ids)

    def __add_assay(self, part_ids, substrate, assay_ids):
        '''Add assay.'''
        assay_id = tuple(part_ids + [substrate])
        assay_ids.append(assay_id)
        count = str(Counter(assay_ids)[assay_id])

        assay = self._add_vertex('_'.join(part_ids + [substrate, count]),
                                 {'is_reagent': False})

        substrate = self._add_vertex(substrate, {'is_reagent': False})

        self._add_edge(substrate, assay, {'Volume': 1.0})

        for part_id in part_ids:
            part = self._add_vertex(part_id + '_lys',
                                    {'is_reagent': False})

            self._add_edge(part, assay, {'Volume': 19.0 / len(part_ids)})


def _get_substrate_plate(wklst_df, substrates, name='substrate_treatment'):
    '''Get substrate plate.'''
    substrates_df = wklst_df[wklst_df['ComponentName'].isin(substrates)]
    substrates_df = substrates_df[['ComponentName', 'DestinationPlateWell']]
    substrates_df.columns = ['id', 'well']
    return plate.from_table(substrates_df, name)


def main(args):
    '''main method.'''
    recipe_df = pd.read_csv(args[0], dtype=str)

    input_plates = pipeline.get_input_plates(args[2])

    dte = strftime("%y%m%d", gmtime())

    for name, group_df in recipe_df.groupby('Project'):
        out_dir_name = os.path.join(os.path.join(args[1], dte + args[3]), name)

        writers = [EnzymeScreenWriter(group_df, args[5:],
                                      dte + 'ENZ' + name[:3].upper())]

        pipeline.run(writers, input_plates, {'reagents': args[4]},
                     out_dir_name)

        wklst_df = worklist.format_worklist(out_dir_name)
        plt = _get_substrate_plate(wklst_df, group_df['Substrate'].unique())
        plt.to_csv(out_dir_name)


if __name__ == '__main__':
    main(sys.argv[1:])
