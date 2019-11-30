#!/usr/bin/env python3

import sys

args = sys.argv

if len(args) != 7:

	print('''
		Replaces entries in the field specified by -field in the file
		specified by -file with the second field of the row in the file
		provided by -map for which the first field matches. Assumes tab
		delimited input.

		Example:

		applyMap2table.py -field 1 -file file.txt -map map.txt

		[file.txt]
		A	B
		C	D

		[map.txt]
		A	aa
		C	cc

		[output]
		aa	B
		cc	D


		''', file=sys.stderr)

	sys.exit()


mapFilepath = args[args.index('-map')+1]
inputFilepath = args[args.index('-file')+1]
field = int(args[args.index('-field')+1]) -1

Map = { line.split('\t')[0]:line.split('\t')[1] for line in open(mapFilepath).read().strip().split('\n') }

#for k in Map:
#	print(k, Map[k])
#sys.exit()


with open(inputFilepath) as inFl:
	for line in inFl:
		contents = line.strip().split('\t')

		if contents[field] in Map:
			contents[field] = Map[contents[field]]
			print('\t'.join(contents))
		else:
			print('Not found in map:\t{0}'.format(contents[field]), file=sys.stderr)
			print(line, end='')
