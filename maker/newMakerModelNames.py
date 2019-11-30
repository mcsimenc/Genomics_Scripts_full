#!/usr/bin/env python3

import re
import sys

def help():
	print('''
		Usage:
		------------
		newMakerModelNames.py -f <maker_gff> -p <prefix_string>

		Description:
		------------
		Renames ID, Name, and Parent attributes for gene, mRNA,
		exon, CDS, five_prime_UTR, and three_prime_UTR features
		in a MAKER-generated GFF3 file as follows, with the numerical
		part of the name of successive features incremented by 1.
		The first mRNA, CDS, exon, and UTR feature associated with a
		given gene will always be numered 0, while genes will not
		be numbered based on sequence position (i.e. the only gene
		numbered 0 will be on the first sequence/scaffold/contig).
		Below, seq_name is the sequence on which feature occurs:

		gene	ID=seq_name_G000000
			Name=seq_name_G000000

		mRNA	ID=seq_name_G000000_mRNA_00
			Name=seq_name_G000000_mRNA_00
			Parent=seq_name_G000000

		exon	ID=seq_name_G000000_exon_00
			Name=seq_name_G000000_exon_00
			Parent=seq_name_G000000_mRNA_00

		CDS	ID=seq_name_G000000_CDS_00
			Name=seq_name_G000000_CDS_00
			Parent=seq_name_G000000

		five_prime_UTR	ID=seq_name_G000000_5UTR_00
				Name=seq_name_G000000_5UTR_00
				Parent=seq_name_G000000_mRNA_00

		three_prime_UTR	ID=seq_name_G000000_3UTR_00
				Name=seq_name_G000000_3UTR_00
				Parent=seq_name_G000000_mRNA_00

		Options:
		------------
		-f <str>	Path to MAKER GFF3 file.
	
		-p <str>	Prefix for new names.


		Output:
		------------
		Prints GFF3 lines to stdout. Line ordering is preserved.

		Prints mapping of old IDs to new ones to stderr.
		
		''')
	sys.exit(0)


args = sys.argv

if '-f' not in args or '-p' not in args or len(args) != 5:
	help()

# parse command line arguments
infl = args[args.index('-f') + 1 ]
prefix = args[args.index('-p') + 1 ]

# compile regex patterns
rp_id = re.compile('ID=(.+?)(?=;|$)')
rp_name = re.compile('Name=(.+?)(?=;|$)')
rp_parent = re.compile('Parent=(.+?)(?=;|$)')
rp_seq_name = re.compile('(^.+?)(?=\s)')



with open(infl) as gff:

	for line in gff:

		if 'maker\tgene' in line:

			seq_name = re.search(rp_seq_name, line).group(1)

			new_id = '{0}_G{1}'.format(seq_name, gene_number.zfill(6))
			
			id_indices = re.search(rp_id, line).span(1)

			gene_number += 1
			

		elif 'maker\tmRNA' in line:
			print(line, end='')

		elif 'maker\texon' in line:
			print(line, end='')

		elif 'maker\tCDS' in line:
			print(line, end='')

		elif 'maker\tfive_prime_UTR' in line:
			print(line, end='')

		elif 'maker\tthree_prime_UTR' in line:
			print(line, end='')

		else:
			continue
