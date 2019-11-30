#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		python3 split_fasta_seqs.py [input_file] [out_prefix]

		Description:
		------------
		Outputs FASTA files each containing a unique sequenced derived from
		each sequence in the FASTA file [input_file]. Output files will be
		written to the location specified by [out_prefix].fasta
		''')
	sys.exit(0)


args = sys.argv

if 'help' in args or 'h' in args or len(args) < 2:
	help()

in_fl = open(args[1])

try:
	out_prefix = args[2]
except IndexError:
	out_prefix = in_fl

seq = 0
for line in in_fl:
	if line.startswith('>'):
		seq += 1
		out_fl = open(out_prefix + "_" + str(seq) + ".fasta", "w")
		out_fl.write(line)
	else:
		out_fl.write(line)

out_fl.close()
