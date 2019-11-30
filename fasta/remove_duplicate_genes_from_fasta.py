#!/usr/bin/env python3

import sys
from Bio import SeqIO

args = sys.argv

if len(args) < 2:

	print('''
		usage:
			remove_duplicate_genes_from_fasta.py	<fasta>

		This script checks for sequences in a fasta file that are identical or
		substrings of each other and removes the shorter sequences. If sequences
		are non-identical and not substrings of each other then this script will
		remove both sequences. A log file explaining what was removed is output
		as duplicate_genes.log
		''', file=sys.stderr)

	sys.exit()



fasta_flpath = args[1]

fasta_fl = list(SeqIO.parse(fasta_flpath, 'fasta'))

to_remove_substr = []

to_remove_identical = []

to_remove_nonidentical = []


# Remove a seq if it is a substring or identical to a seq from the same taxon

checked = set()

#for seq_obj_1 in fasta_fl:
for i in range(len(fasta_fl)):

	seq_obj_1 = fasta_fl[i]

	#for seq_obj_2 in fasta_fl:
	for j in range(len(fasta_fl)):

		seq_obj_2 = fasta_fl[j]

		if not seq_obj_1.name == seq_obj_2.name:

			taxon1 = str(seq_obj_1.name).split('_')[0]

			taxon2 = str(seq_obj_2.name).split('_')[0]

			name1 = str(seq_obj_1.name)

			name2 = str(seq_obj_2.name)

			if taxon1 == taxon2:

				seq1 = str(seq_obj_1.seq)

				seq2 = str(seq_obj_2.seq)

				if not (name1, name2) in checked:

					checked.add((name1, name2))

					if seq1 in seq2:

						if len(seq1) < len(seq2):

							to_remove_substr.append( (i, j, seq_obj_1.name, seq_obj_2.name) )

						elif len(seq1) == len(seq2):

							to_remove_identical.append( (i, j, seq_obj_1.name, seq_obj_2.name) )

checked = set()

# Remove non-identical seqs with the same name

#for seq_obj_1 in fasta_fl:
for i in range(len(fasta_fl)):

	seq_obj_1 = fasta_fl[i]

	#for seq_obj_2 in fasta_fl:
	for j in range(len(fasta_fl)):

		seq_obj_2 = fasta_fl[j]

		if not seq_obj_1.name == seq_obj_2.name:

			taxon_gene_1 = str(seq_obj_1.name).split('_')[0:2]

			taxon_gene_2 = str(seq_obj_2.name).split('_')[0:2]

			name1 = str(seq_obj_1.name)

			name2 = str(seq_obj_2.name)

			if taxon_gene_1 == taxon_gene_2:

				seq1 = str(seq_obj_1.seq)

				seq2 = str(seq_obj_2.seq)

				if not (name1, name2) in checked:

					checked.add((name1, name2))

					if not seq1 == seq2:

						to_remove_identical.append( (i, j, seq_obj_1.name, seq_obj_2.name) )

# remove seqs and write to log file

with open('duplicate_genes.log','w') as log_fl:

	for item in to_remove_substr:

		name1 = item[2]

		name2 = item[3]

		log_fl.write('{0}\tnonidentical_substring_of\t{1}\n'.format(name1, name2))

	for item in to_remove_identical:

		name1 = item[2]

		name2 = item[3]

		log_fl.write('{0}\tidentical_to\t{1}\n'.format(name1, name2))

	for item in to_remove_nonidentical:

		name1 = item[2]

		name2 = item[3]

		log_fl.write('{0}\tboth_removed_nonidentical_nonsubstrings\t{1}\n'.format(name1, name2))

indices_to_remove = set([ item[0] for item in to_remove_substr ] + [ item[0] for item in to_remove_identical ] + [ item[0] for item in to_remove_nonidentical ]  + [ item[1] for item in to_remove_nonidentical ] )

new_fasta_fl = [ fasta_fl[i] for i in indices_to_remove ]

SeqIO.write(new_fasta_fl, 'removed_duplicate_genes.fasta', 'fasta')
