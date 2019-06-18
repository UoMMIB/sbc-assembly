# sbc-assembly

For initial environment setup:

1. Install Vienna RNA (see https://anaconda.org/bioconda/viennarna).
2. Install NCBI Blast (see https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download).

## LCR2

This script assumes that PlasmidGenie has been used to add the necessary
entries into the ICE database.

1. Amend the script `lcr2.sh`, updating ICE URL, username and password, as well
as ICE ids to assemble. The optional three-letter code for naming the worklist,
currently with a default of `LCR`, may also be updated.

2. Ensure that all necessary source plates are in the `data/plates` directory.
Plates that are required include those containing plasmid parts (i.e. individual
parts within the plasmids, typically that which is returned from Twist), and
those containing primers (these primers are *not* held in ICE, and must be
specified here, using the naming convention of `[PART_PLASMID_ID]_P` and
`[PART_PLASMID_ID]_NP` for phosphorylated and non-phosphorylated primers
respectively. Plates can be defined in one of two formats (see
`data/plates/12135272.csv` and `data/plates/11276738.csv`) for examples of each
format.

3. Run the script through the command: `bash lcr2.sh`.


## ENZYME SCREENING

This script reads a manually-generated screening list, and from which generates
appropriate worklists.

See `data/enz_scr/enz_scr.csv` for an example of such a screening list.

1. Amend the script `enz_scr.sh` to update the location of the enzyme screening
list, and the optional three-letter code for naming the worklist, which
currently has a default of `ENZ`.

2. Run the script through the command: `bash enz_scr.sh`.
