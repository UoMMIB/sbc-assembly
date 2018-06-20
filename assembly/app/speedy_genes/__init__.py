'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''


def get_dil_oligo_id(oligo_id):
    '''Get diluted oligo id.'''
    return oligo_id if oligo_id[-1] == 'm' else oligo_id + '_dil'
