#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		filter_blastp.py -b <blast_output> -floor <min_identity> -ceiling <max_identity>

		Description:
		------------
		Outputs lines of alignments from blast_output (outfmt 6) for which
		the percent identity falls between -floor and -ceiling (defaults 0
		100).

		Options:
		------------
		-justOne	For alignments whose percent identity is within the threshold
				specified by -ceiling and/or -floor
		
		''')
	sys.exit(0)

args = sys.argv

if '-b' not in args or '-h' in args:
	help()
else:
	infl = args[ args.index('-b') + 1 ]

if '-floor' in args:
	floor = float(args[ args.index('-floor') + 1 ])
else:
	floor = float(0)

if '-ceiling' in args:
	ceiling = float(args[ args.index('-ceiling') + 1 ])
else:
	ceiling = float(100)

seqset = set()

with open(infl) as fl:

	for line in fl:
		contents = line.strip().split('\t')
		id = float(contents[2])
		if id <= ceiling and id >=floor:

			if '-justOne' not in args:
				print(line, end='')
				#print('{0}\t{1}'.format(contents[0], contents[1]))
			else:
				seqset.add(frozenset([contents[0],contents[1]]))

if '-justOne' in args:
	seqs = [ list(pair) for pair in seqset ]
	for pair in seqs:
		print(pair[0])
