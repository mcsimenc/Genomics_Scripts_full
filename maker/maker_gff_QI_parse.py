#!/usr/bin/env python3

import sys


def help():
	print('''
		Usage:
		------------
		maker_gff_QI_parse.py -gff <filepath>

		Description:
		------------
		Prints the QI information from the attribute column of mRNA features in a
		MAKER-generated GFF3 as tab-delimited text with the following fields in the
		following order:

		ID
		AED (nucleotide AED)
		eAED (exon AED)
		Length of the 5' UTR
		Fraction of splice sites confirmed by an EST alignment
		Fraction of exons that overlap an EST alignment
		Fraction of exons that overlap EST or Protein alignments
		Fraction of splice sites confirmed by a SNAP prediction
		Fraction of exons that overlap a SNAP prediction
		Number of exons in the mRNA
		Length of the 3' UTR
		Length of the protein sequence produced by the mRNA

		Options:
		------------
		-gff	Path to the gff file to parse

		''')
	sys.exit(0)

args = sys.argv

if not '-gff' in args or len(args) != 3:
	help()

in_fl_pth = args[args.index('-gff') + 1]

print('ID\tAED\teAED\t5\'_UTR_len\tfrac_ss_with_transcript_support\tfrac_exons_with_transcript_support\tfrac_exons_with_transc_or_prot_support\tfrac_ss_with_SNAP_support\tfrac_exons_with_SNAP_support\tnum_exons\t3\'_UTR_len\tprot_len')

with open(in_fl_pth) as in_fl:
	for line in in_fl:
		if '\tmRNA\t' in line:
			fields = line.strip().split('\t')
			attributes = fields[8].split(';')
			ID = attributes[0].split('=')[1]
			AED = attributes[3].split('=')[1]
			eAED = attributes[4].split('=')[1]
			QI = attributes[5].split('|')
			QI[0] = QI[0].split('=')[1]
			print('{0}\t{1}\t{2}\t{3}'.format(ID, AED, eAED, '\t'.join(QI)))
