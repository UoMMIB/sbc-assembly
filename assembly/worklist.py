'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=not-an-iterable
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=ungrouped-imports
# pylint: disable=unsubscriptable-object
# pylint: disable=wrong-import-order
from operator import itemgetter
import os

from scipy.spatial.distance import cityblock
from synbiochem.utils.graph_utils import get_roots

from assembly import plate
import pandas as pd


_VALUES_RENAME = {('src_plate', 'dest_plate'):
                  {('reagents'): 'MastermixTrough'}}

_COLUMNS_RENAME = {'src_name': 'ComponentName',
                   'src_plate': 'SourcePlateBarcode',
                   'src_well': 'SourcePlateWell',
                   'dest_plate': 'DestinationPlateBarcode',
                   'dest_well': 'DestinationPlateWell'}

_COLUMNS_ORDER = ['Volume',
                  'SourcePlateBarcode',
                  'SourcePlateWell',
                  'DestinationPlateBarcode',
                  'DestinationPlateWell',
                  'ComponentName']


class WorklistGenerator(object):
    '''Class to generate worklists.'''

    def __init__(self, graph):
        self.__graph = graph
        self.__worklist = None
        self.__input_plates = {}
        self.__plate_names = {'reagents': 'reagents',
                              'output': 'output'}
        self.__added_comps = {}

    def get_worklist(self, input_plates=None, plate_names=None):
        '''Gets worklist and input_plates.'''
        if not self.__worklist:
            self.__create_worklist(input_plates, plate_names)

        return self.__worklist, self.__input_plates

    def __create_worklist(self, input_plates, plate_names):
        '''Creates worklist and plates.'''
        data = []

        if input_plates:
            self.__input_plates.update(input_plates)

        if plate_names:
            self.__plate_names.update(plate_names)

        for root in get_roots(self.__graph):
            self.__traverse(root, 0, data)

        self.__worklist = pd.DataFrame(data)

        self.__write_input_plates()
        self.__add_locations()

    def __write_input_plates(self):
        '''Writes input_plates from worklist.'''
        # Write input plate:
        if 'src_well_fixed' not in self.__worklist:
            self.__worklist['src_well_fixed'] = None

        if 'dest_well_fixed' not in self.__worklist:
            self.__worklist['dest_well_fixed'] = None

        inpt = \
            self.__worklist.loc[self.__worklist['src_is_input']
                                ][['src_name', 'src_well_fixed']].values

        for val in inpt:
            self.__add_component(val[0],
                                 'input',
                                 False,
                                 val[1])

        # Write reagents plate:
        reags = \
            self.__worklist.loc[self.__worklist['src_is_reagent']
                                ][['src_name', 'src_well_fixed']].values

        for val in sorted(reags, key=itemgetter(0)):
            self.__add_component(val[0],
                                 self.__plate_names['reagents'],
                                 True,
                                 val[1])

        # Write intermediates:
        intrm = self.__worklist[~(self.__worklist['src_is_input']) &
                                ~(self.__worklist['src_is_reagent'])]

        for _, row in intrm.sort_values('level', ascending=False).iterrows():
            self.__add_component(row['src_name'],
                                 row['level'],
                                 False,
                                 row['src_well_fixed'])

        # Write products:
        for _, row in self.__worklist.iterrows():
            if row['level'] == 0:
                self.__add_component(row['dest_name'],
                                     self.__plate_names['output'],
                                     False,
                                     row['dest_well_fixed'])

    def __add_locations(self):
        '''Add locations to worklist.'''
        locations = self.__worklist.apply(lambda row: self.__get_location(
            row['src_name'], row['dest_name']), axis=1)

        loc_df = locations.apply(pd.Series)
        loc_df.index = self.__worklist.index
        loc_df.columns = ['src_plate',
                          'src_well',
                          'src_idx',
                          'dest_plate',
                          'dest_well',
                          'dest_idx']

        self.__worklist = pd.concat([self.__worklist, loc_df], axis=1)
        self.__worklist.sort_values(['level',
                                     'src_is_reagent',
                                     'src_plate',
                                     'src_idx',
                                     'dest_idx'],
                                    ascending=[False, False, True, True, True],
                                    inplace=True)

    def __get_location(self, src_name, dest_name):
        '''Get location.'''
        srcs = self.__added_comps[src_name]
        dests = self.__added_comps[dest_name]

        shortest_dist = float('inf')
        optimal_pair = None

        for src_plt, src_wells in srcs.items():
            for dest_plt, dest_wells in dests.items():
                for src_well in src_wells:
                    for dest_well in dest_wells:
                        src_ind = plate.get_indices(src_well)
                        dest_ind = plate.get_indices(dest_well)
                        dist = cityblock(src_ind, dest_ind)

                        if dist < shortest_dist:
                            src_idx = \
                                self.__input_plates[src_plt].get_idx(*src_ind)
                            dest_idx = \
                                self.__input_plates[dest_plt].get_idx(
                                    *dest_ind)
                            shortest_dist = dist
                            optimal_pair = [src_plt, src_well, src_idx,
                                            dest_plt, dest_well, dest_idx]
        return optimal_pair

    def __traverse(self, dest, level, data):
        '''Traverse tree.'''
        for src in dest.predecessors():
            edge_idx = self.__graph.get_eid(src.index, dest.index)
            edge = self.__graph.es[edge_idx]

            opr = edge.attributes()

            for key, val in src.attributes().items():
                opr['src_' + key] = val

            for key, val in dest.attributes().items():
                opr['dest_' + key] = val

            opr['level'] = level
            opr['src_is_input'] = not src.indegree() and not src['is_reagent']

            data.append(opr)
            self.__traverse(src, level + 1, data)

    def __add_component(self, component, plate_id, is_reagent, well_name):
        '''Add component.'''
        if component not in self.__added_comps:
            (well, plt) = plate.add_component({'id': component},
                                              plate_id,
                                              is_reagent,
                                              self.__input_plates,
                                              well_name)

            self.__added_comps[component] = {plt.get_name(): [well]}


def to_csv(wrklst, out_dir_name='.'):
    '''Export worklist as csv file.'''
    filepath = os.path.abspath(os.path.join(out_dir_name,
                                            'worklist.csv'))
    wrklst.to_csv(filepath, encoding='utf-8', index=False)


def format_worklist(dir_name):
    '''Rename columns to SYNBIOCHEM-specific headers.'''

    for(dirpath, _, filenames) in os.walk(dir_name):
        for filename in filenames:
            if filename == 'worklist.csv':
                filepath = os.path.join(dirpath, filename)
                df = pd.read_csv(filepath)
                _rename_values(df)
                _rename_cols(df)
                df = _reorder_cols(df)
                df.to_csv(filepath, encoding='utf-8', index=False)


def _rename_values(df):
    '''Rename values.'''
    for columns, replacement in _VALUES_RENAME.items():
        for to_replace, value in replacement.items():
            df[list(columns)] = df[list(columns)].replace(to_replace, value)


def _rename_cols(df):
    '''Rename cols.'''
    df.rename(columns=_COLUMNS_RENAME, inplace=True)


def _reorder_cols(df):
    '''Reorder cols.'''
    columns = _COLUMNS_ORDER + \
        sorted([col for col in df.columns if col not in _COLUMNS_ORDER])

    return df.reindex(columns, axis=1)
