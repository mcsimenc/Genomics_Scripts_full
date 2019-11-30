#!/usr/bin/env python3

import sys

args = sys.argv

if not len(args) == 3:

	print('''
		usage:
			rename_fasta_seqheaders.py <fasta> <map>



		Renames seq headers in fasta file according to mapping provided as <map>

		<map>
			a two-column file where first col is the old name and second col is new name

		''', file=sys.stderr)

	sys.exit()

map_dct = {}

# read in mapping
with open(args[2]) as in_fl:

	for line in in_fl:

		old, new = line.strip().split('\t')

		map_dct[old] = new

with open(args[1]) as in_fl:

	for line in in_fl:

		if line.startswith('>'):

			old = line.strip().lstrip('>')

			try:

				new = '>{0}'.format(map_dct[old])

				print(new)

			except KeyError:

				print('NOT_FOUND_IN_MAPPING_FILE\t{0}'.format(old), file=sys.stderr)
				print(line, end='')

		else:

			print(line, end='')
