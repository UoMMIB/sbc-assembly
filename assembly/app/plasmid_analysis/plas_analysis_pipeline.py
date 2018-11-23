'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import sys

from assembly import plate
import pandas as pd


def main(args):
    '''main method.'''
    colony_df = pd.read_csv(args[0])
    plates = []

    for idx, plate_df in colony_df.groupby('DWPBarcode'):
        plate_df = plate_df[['DWPWell', 'ColonyID']]
        plate_df.columns = ['well', 'id']
        plates.append(plate.from_table(plate_df, idx))

    print(plates)


if __name__ == '__main__':
    main(sys.argv[1:])
