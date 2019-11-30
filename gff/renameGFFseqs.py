#!/usr/bin/env python3

import sys


def help():
	print('''
		Usage:
		------------
		renameGFFseqs.py -map <file> -input <file>

		Description:
		------------
		Renames seq ids (column 1) in a GFF3 file according to
		a two column mapping file given by -map.

		Output:
		------------
		Modified lines from input GFF3 printed to stdout.

		''')

	sys.exit()

args = sys.argv

if '-h' in args or len(args) < 5 or '-map' not in args or '-input' not in args:
	help()

map_flname = args[args.index('-map') + 1]
in_flname = args[args.index('-input') + 1]


map_dct = {}
with open(map_flname) as map_fl:
	for line in map_fl:
		contents = line.strip().split('\t')
		try:
			from_id = contents[0]
			to_id = contents[1]
		except KeyError:
			continue

		if from_id in map_dct:
			print('Duplicate ID in first column: {0}'.format(from_id))

		else:
			map_dct[from_id] = to_id

with open(in_flname) as input_file:
	for line in input_file:
		if  line.startswith('##sequence-region'):
			contents = line.strip().split()
			contents[1] = map_dct[contents[1]]
			print('{0}\t{1}'.format(contents[0], ' '.join(contents[1:])))
		elif line.startswith('#'):
			print(line)
		else:
			contents = line.strip().split()
			contents[0] = map_dct[contents[0]]
			print('\t'.join(contents))
