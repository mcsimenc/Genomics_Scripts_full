#!/usr/bin/env python3

import sys
from Bio import SeqIO

def help():
	print('''
		Usage:
		------------
		count_masked_genes.py <fasta>

		Description:
		------------
		Outputs information about amount of masking of sequences in <fasta>.
		Interprets Ns as hard-masked nucleotides, lowercase 'nactg's as soft-
		masked nucleotides, and 'ACTG' as unmasked nucleotides. This script
		reports:

		1. Proportion of sequences with any amount of hard-masking
		2. Proportion of sequences with any amount soft-masking
		3. Proportion of sequences with any amount masking
		4. Proportion hard-masked nucleotides among all sequences
		5. Proportion soft-masked nucleotides among all sequences
		6. Proportion masked nucleotides among all sequences

		**Requires BioPython for Python3

		''')
	sys.exit(0)


args = sys.argv
if len(args) < 2 or '-h' in args or '-help' in args:
	help()

masking_stats = {'num_nt':0, 'seqs_hard_masked':0, 'seqs_soft_masked':0, 'seqs_not_masked':0, 'nt_hard_masked':0, 'nt_soft_masked':0, 'nt_not_masked':0}


seq_record_object = SeqIO.parse(args[1], 'fasta')
num_seqs = 0

for seq_record in seq_record_object:

	num_seqs += 1
	seq = str(seq_record.seq)

	# check if any part of sequence is masked
	if 'N' in seq:
		masking_stats['seqs_hard_masked'] += 1
	elif 'n' in seq or 'a' in seq or 'c' in seq or 't' in seq or 'g' in seq:
		masking_stats['seqs_soft_masked'] += 1
	else:
		masking_stats['seqs_not_masked'] += 1
		

	for nt in seq:
		masking_stats['num_nt'] += 1

		if nt=='N':
			masking_stats['nt_hard_masked'] += 1
		elif nt in 'nactg':
			masking_stats['nt_soft_masked'] += 1
		elif nt in 'ACTG':
			masking_stats['nt_not_masked'] += 1


print('total_seqs\tseqs_hard_masked\tseqs_soft_masked\tseqs_not_masked\ttotal_nucleotides\thard_masked_nucleotides\tsoft_masked_nucleotides\tunmasked_nucleotides')
print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(num_seqs, masking_stats['seqs_hard_masked'], masking_stats['seqs_soft_masked'], masking_stats['seqs_not_masked'], masking_stats['num_nt'], masking_stats['nt_hard_masked'], masking_stats['nt_soft_masked'], masking_stats['nt_not_masked']))
