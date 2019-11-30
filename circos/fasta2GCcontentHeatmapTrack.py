#!/usr/bin/env python3

# If you have questions about this script or something doesn't work right you can email Matt at mcsimenc@gmail.com

import sys
from math import ceil

def help():
	print('''

		Usage:
		------------
		fasta2GCcontentHeatmapTrack.py -window <int> -fasta <file> [-scafList <file>]

		Description:
		------------
		Takes a fasta input and a window and outputs gc content for that window as a decimal
		fraction. Optionally restrict output to certain seqs with -scafList

		Options:
		------------
		-fasta		<path>	FASTA file

		-window	    	<int>	The number of bases in the sliding window 
		
		-scafList 	<path>	Output only seqs in this list


		Output:
		------------
		scaf	start	stop	density

''', file=sys.stderr)



def genWindowCoords(n, windowLen):
	return (n*windowLen, (n+1)*windowLen-1)

def seq2gc(seq):
	seq = seq.lower()
	return (seq.count('g') + seq.count('c'))/len(seq)

def seq2gcHeatmap(seqName, seq, windowLen):

	seqLen = len(seq)
	numWindows = ceil(seqLen//windowLen)

	for i in range(numWindows):
		window = genWindowCoords(i, windowLen)
		gc = seq2gc(seq[window[0]:window[1]+1])
		print('{0}\t{1}\t{2}\t{3}'.format(seqName, window[0], window[1], gc))

	window = genWindowCoords(numWindows, windowLen)
	gc = seq2gc(seq[window[0]:seqLen])
	print('{0}\t{1}\t{2}\t{3}'.format(seqName, window[0], seqLen, gc))




args = sys.argv

if '-h' in args or len(args) < 5 or ('-fasta' not in args or '-window' not in args):
	help()
	sys.exit()

if '-scafList' in args:
	scafListFl = args[args.index('-scafList') +1]
	scafList = open(scafListFl).read().strip().split('\n')
else:
	scafList = None

windowLen = int(args[args.index('-window') +1])
fasta_filepath = args[args.index('-fasta') +1]


seq = ''
seqName = ''
with open(fasta_filepath) as fastaFl:
	for line in fastaFl:
		if line.startswith('>'):
			if seq != '':
				if scafList != None:
					if seqName in scafList:
						seq2gcHeatmap(seqName, seq, windowLen)
				else:
					seq2gcHeatmap(seqName, seq, windowLen)
			seqName = line.strip()[1:]
			seq = ''
		else:
			seq += line.strip()


	if scafList != None:
		if seqName in scafList:
			seq2gcHeatmap(seqName, seq, windowLen)
	else:
		seq2gcHeatmap(seqName, seq, windowLen)
