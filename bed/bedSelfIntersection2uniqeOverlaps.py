#!/usr/bin/env python3


import sys

def help():
	print('''
		Usage:
		------------
		bedSelfIntersection2uniqeOverlaps.py -bed <bedfile>

		Description:
		------------
		This is to be run following doing an intersection of
		a BED with itself. It will remove self-matching lines
		and redundant matches. The command generating the bed
		should have been:

		intersectBed -a A.bed -b B.bed -wa -wb > intersection.bed

		''')
	sys.exit(0)


args = sys.argv

if '-bed' not in args or len(args) != 3:
	help()

infl = args[args.index('-bed') + 1]

outSet = set()
with open(infl) as bed:

	for line in bed:
		contents = line.strip().split('\t')
		a = '\t'.join(contents[:10])
		b = '\t'.join(contents [10:])

		if a==b:
			continue
		else:
			
			outSet.add(frozenset([a,b]))


for pair in outSet:
	pair = list(pair)
	print('{0}\t{1}'.format(pair[0], pair[1]))
