#!/usr/bin/env python3

import sys


def help():
	print('''
		Usage:
		------------
		python3 ./generate_fasta_qual.py [fasta_file] [out_file]

		Description:
		------------
		Outputs a file [out_file] with quality scores of 99
		for every nucleotide in the fasta file.
		''')
	sys.exit(0)


args = sys.argv

if 'help' in args or 'h' in args or len(args) < 3:
	help()


in_fl = open(args[1], 'r')
out_fl = open(args[2], 'w')


for line in in_fl:
	if line.startswith('>'):
		out_fl.write(line)
	else:
		out_fl.write('99 ' * (len(line)-1))
		out_fl.write('\n')


in_fl.close()
out_fl.close()
