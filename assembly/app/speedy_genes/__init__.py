'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''


def get_dil_oligo_id(oligo_id):
    '''Get diluted oligo id.'''
    return oligo_id if oligo_id[-1] == 'm' else oligo_id + '_dil'


def get_block_id(block_idx, block):
    '''Get block id.'''
    mutations = [oligo[:-1] for oligo in block if oligo[-1] == 'm']

    return str(block_idx + 1) + '_' + \
        ('&'.join(mutations) if mutations else 'wt')


def get_design_id(design):
    '''Get design id.'''
    return '-'.join([get_block_id(block_idx, block)
                     for block_idx, block in enumerate(design)])
