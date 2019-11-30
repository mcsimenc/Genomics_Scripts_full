#!/usr/bin/env python3

import sys
from Bio import SeqIO

def help():
	print('''
		Usage:
		------------
		python3 merge_cds_in_fasta.py -i [input_fasta] -o [output_fasta] [options]

		Description:
		------------
		Merges entries in the input fasta file with the same name, outputting
		a nucleotide or translated nucleotide fasta depending on options.

		Options:
		------------
		-i	input file
		-o	output file
		-t	translate nucleotide sequences
		''')
	sys.exit(0)

args = sys.argv

if len(args) < 5:
	help()

in_fl = open(args[args.index('-i')+1],'rU')

out_fl = open(args[args.index('-o')+1],'w')

try:
	translate = args.index('-t')
except ValueError:
	translate = False



fasta=SeqIO.parse(in_fl,'fasta')

merged_seqs = {}

for entry in fasta:

	if not entry.id in merged_seqs:
		merged_seqs[entry.id] = entry
	else:
		merged_seqs[entry.id].seq = merged_seqs[entry.id].seq + entry.seq


outpt = []
for id in merged_seqs:
	if translate:
		merged_seqs[id].seq = merged_seqs[id].seq.translate()
		outpt.append(merged_seqs[id])
	else:
		outpt.append(merged_seqs[id])

SeqIO.write(outpt, out_fl, 'fasta')
