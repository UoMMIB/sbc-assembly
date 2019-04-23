from opentrons import labware, instruments, robot


def run_custom_protocol(
        transfer_volume=20,
        source_container='96-flat',
        destination_container='96-flat'):

    # Load labware
    tip_racks = [labware.load('tiprack-200ul', slot) for slot in ['11']]

    p50multi = instruments.P50_Multi(mount='right', tip_racks=tip_racks)

    source_plate = labware.load(source_container, '1')
    dest_plate = labware.load(destination_container, '2')

    col_count = len(dest_plate.cols())

    p50multi.pick_up_tip()

    for col_index in range(col_count):
        source_well = source_plate.cols(1)
        dest_wells = dest_plate.cols(col_index)

        p50multi.distribute(
            transfer_volume,
            source_well,
            dest_wells,
            new_tip='never')

    p50multi.drop_tip()


run_custom_protocol()

for command in robot.commands():
    print(command)
