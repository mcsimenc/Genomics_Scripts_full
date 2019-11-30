#!/usr/bin/env python3

import sys

def help():
	print('''
	usage:
		gffNewGFFforEachAnticodon_tRNAscanFeatures.py [-pseudo] < GFF3file


	description: Writes each tRNA feature to a new GFF3 file named as its anticodon.
		     by default only non-pseudogenes are written.

	-pseudo			Write pseudogenes only

		''', file=sys.stderr)
	sys.exit()


args =sys.argv

if '-h' in args:
	help()


for line in sys.stdin:
	if 'trnascan' in line:
		if '\ttRNA\t' in line:
			if not '-pseudo' in args:
				aa_codon = line.strip().split('\t')[8].split(';')[0].split('noncoding-')[1].split('-gene-')[0].split('_')
				aa = aa_codon[0]
				codon = aa_codon[1]
				if not 'Pseudo' in line:
					with open('{0}.gff'.format(aa), 'a') as outFl:
						outFl.write(line)
			else:
				aa_codon = line.strip().split('\t')[8].split(';')[0].split('noncoding-Pseudo_')[1].split('-gene-')[0].split('_')
				aa = aa_codon[0]
				codon = aa_codon[1]
				if 'Pseudo' in line:
					with open('{0}.gff'.format(aa), 'a') as outFl:
						outFl.write(line)
