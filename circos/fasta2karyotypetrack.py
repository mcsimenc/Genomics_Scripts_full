#!/usr/bin/env python3

from Bio import SeqIO
import sys

def help():
	print('''
 usage:
 	fasta2karyotypetrack.py -f <fasta> [-c]
 
 description: 
 	Outputs the lengths of the seqs in <fasta> in Circos track-style

	-c 	Contig names have format Chr01, Chr02, ...
 
		''', file=sys.stderr)
	sys.exit()

def fasta2track(fasta):
	'''
	Returns a list of tuples (seqname, len(seq)) for seqs in fasta
	'''
	seq_lens = sorted([ (seq.name, len(seq)) for seq in SeqIO.parse(fasta, format='fasta') ], key=lambda x:x[0])
	for i, seq in enumerate(seq_lens):
		if '-c' in args:
			chrNum = int(seq[0].lstrip('Chr'))
		else:
			chrNum = i
		print('chr - {0}\t{1}\t0\t{2}\t{3}'.format(chrNum, seq[0], seq[1], i))


if __name__ == '__main__':
	args = sys.argv
	if '-h' in args or '-f' not in args:
		help()
	fastaPth = args[args.index('-f')+1]
	fasta2track(fastaPth)

