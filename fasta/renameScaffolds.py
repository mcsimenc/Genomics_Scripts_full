#!/usr/bin/env python3

import sys

args = sys.argv


def help():
	print('''
		Usage:
		------------
		renameScaffolds.py [options]

		Description:
		------------
		Renames sequences in a fasta file. New sequence names will be assigned to
		sequences sorted by sequence length such that [prefix]0001 is the new name
		of the longest sequence. Outputs a mapping file with old names and the
		corresponding new name.

		Options:
		------------
		-f [filepath] Input file in FASTA format.

		-p [string] New sequence names prefix: seqs will be [string]0001, [string]0002, ...

		-o [string] Output file prefix: [string].fasta, [inputfilename].[string].seqIDmap
		
		''')
	sys.exit(0)

args = sys.argv


if "-h" in args or "-f" not in args or "-p" not in args or "-o" not in args:
	help()

input_filename = args[args.index('-f') + 1]
seqname_prefix = args[args.index('-p') + 1]
output_prefix = args[args.index('-o') + 1]

# Check if input file exists
try:
	in_fl = open(input_filename)
except FileNotFoundError:
	print('\nThe input file was not found.\n')
	sys.exit(1)


# Determine sequence length
name = ''
seq = ''
len_dct = {}
seq_dct = {}
count = False
length = 0

for line in in_fl:
	if line.startswith('>'):
		if count == True:
			len_dct[name]=length
			seq_dct[name]=seq
			name = line.strip()[1:]
			seq = ''
			length = 0

		elif count == False:
			name = line.strip()[1:]
	else:
		count = True
		length += len(line.strip())
		seq += line.strip()

len_dct[name]=length
seq_dct[name]=seq

len_list = [(name, len_dct[name]) for name in len_dct]
len_list = sorted(len_list, key=lambda x:x[1], reverse=True)

in_fl.seek(0)

# Write fasta with new names and write mapping file
seq_number = 1

with open('{0}.fasta'.format(output_prefix), 'w') as out_fl:

	with open('{0}.{1}.fasta.seqIDmap'.format(input_filename,output_prefix), 'w') as map_fl:

		for item in len_list:
			old_seq_name = item[0]
			new_seq_name = seqname_prefix + '{0:04d}'.format(seq_number)
			seq_number += 1

			out_fl.write('>{0}\n'.format(new_seq_name))
			map_fl.write('{0}\t{1}\n'.format(old_seq_name, new_seq_name))

			# Each line of sequence will be 60 char max
			out_seq_split = [ seq_dct[old_seq_name][i:i+60] for i in range(0, len(seq_dct[old_seq_name]), 60) ]
			for subseq in out_seq_split:
				out_fl.write('{0}\n'.format(subseq))
