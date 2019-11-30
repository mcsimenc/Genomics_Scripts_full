#!/usr/bin/env python3

# For separating the MAKER-output GFF3 file into multiple GFF3 files, one for each taxon.

# usage: separateGFF.py < file.gff

# output will be multiple GFF3 files in the same directory the script is run from

import sys

for line in sys.stdin:
	if line.startswith("##FASTA"):
		break
	elif line.startswith("#"):
		continue
	else:
		taxon = line.strip().split('\t')[0].split('_')[0]
		with open('{0}.gff'.format(taxon), 'a') as currentFile:
			currentFile.write(line)
