# sbc-assembly

## LCR2

Note that this script assumes that PlasmidGenie has been used to add the necessary
entries into the ICE database.

1. Amend the script `lcr2.sh`, updating ICE URL, username and password, as well as
ICE ids to assembly.

2. Ensure that all necessary source plates are in the `data/plates` directory.
Plates that are required include those containing plasmid parts (i.e. individual parts
within the plasmids, typically that which is returned from Twist), and those containing
primers (these primers are *not* held in ICE, and must be specified here, using the naming
convention of [PART_PLASMID_ID]_P and [PART_PLASMID_ID]_NP for phosphorylated and non-phosphorylated
primers respectively.

Plates can be defined in one of two formats (see `data/plates/12135272.csv` and `data/plates/11276738.csv`)
for examples of each format.


3. Run the script `lcr2.sh`.