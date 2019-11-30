#!/usr/bin/env python3

import sys
import math

def help():
	print('''
	usage:
		circosDensity2LabelSize.py -c <int> < input.track > output.track


	description: 
		Transforms a density value where 0 < density < 1 into a font_size
		option using: ceiling(density*100). Use -c

	options:

		-c <int>	Column in input file (1-based) with density value.
				Will be replaced ith font_size=val



		''', file=sys.stderr)
	sys.exit()

args = sys.argv

if '-c' not in args or len(args) < 3:
	help()

c = int(args[args.index('-c') + 1]) -1


for line in sys.stdin:
	line = line.strip().split('\t')
	density = float(line[c])
	font_size = math.ceil(density*100)
	line[c] = 'font_size={0}'.format(font_size)
	print('\t'.join(line))
