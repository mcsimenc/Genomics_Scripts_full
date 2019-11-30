#!/usr/bin/env python3


# I think this slits a maker gff into separate gff files, each separate gff file has the lines from the original gff file that have the same part of the scaffold name before the first underscore:
# For example, if the first 3 lines in the maker gff have first columns like: A_123, B_123, B_234, the A_ line and the B_ lines will go in separate gff files
#
# feed maker gff to this script on stdin

import sys

NEXT_TAXON = False

taxon = None

for line in sys.stdin:

	if line.startswith('###') or  line.startswith('##gff-version'):

		NEXT_TAXON = True

	elif line.startswith('##FASTA'):

		break

	else:

		if NEXT_TAXON:

			fields = line.strip().split('\t')

			taxon = fields[0].split('_')[0]

			with open('{0}.MAKER.gff'.format(taxon), 'a') as out_fl:

				out_fl.write(line)

		else:

			with open('{0}.MAKER.gff'.format(taxon), 'a') as out_fl:

				out_fl.write(line)
