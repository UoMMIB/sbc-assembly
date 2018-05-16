'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import os
import sys
from time import gmtime, strftime

from assembly import pipeline, plate
from assembly.app.lcr import lcr, part_pcr, part_qc, part_dig, utils


def main(args):
    '''main method.'''
    assert len(args[3]) < 4

    ice_helper = utils.ICEHelper(args[0], args[1], args[2])
    plasmid_parts = ice_helper.get_plasmid_parts(args[7:])
    parts_ice = {ice_id: part_ice
                 for _, parts_map in plasmid_parts.iteritems()
                 for ice_id, part_ice in parts_map.iteritems()
                 if part_ice.get_parameter('Type') != 'DOMINO'}
    part_ids = parts_ice.keys()

    dte = strftime("%y%m%d", gmtime())

    writers = [part_pcr.SpecificPartPcrWriter(parts_ice, ice_helper,
                                              dte + 'PCR' + args[3]),
               part_dig.PartDigestWriter(part_ids, dte + 'DIG' + args[3]),
               [part_qc.PartQcWriter(part_ids, dte + 'FPT' + args[3]),
                lcr.LcrWriter(plasmid_parts, dte + 'LCR' + args[3])]]

    input_plates = {}

    for(dirpath, _, filenames) in os.walk(args[4]):
        for filename in filenames:
            if filename[-4:] == '.csv':
                plt = plate.from_table(os.path.join(dirpath, filename))
                input_plates[plt.get_name()] = plt

    out_dir_name = os.path.join(args[6], dte + args[3])
    pipeline.run(writers, input_plates, {'reagents': args[5]}, out_dir_name)

    utils.rename_cols(out_dir_name)


if __name__ == '__main__':
    main(sys.argv[1:])
