#!/usr/bin/env python3

# If you have questions about this script or something doesn't work right you can email Matt at mcsimenc@gmail.com

import sys
import os

def help():
	print('''

	Usage:
	------------
	fixTrackLabels.py -track <file> -karyotype <file>

	Description:
	------------
	Replaces track labels with integer IDs found in karyotype file.

''', file=sys.stderr)

args = sys.argv

if not '-track' in args and not '-karyotype' in args:
	help()
	sys.exit()


trackFl = args[args.index('-track') +1]
karyotypeFl = args[args.index('-karyotype') +1]

_map = {}
with open(karyotypeFl, 'r') as inFl:
	for line in inFl:
		_line = line.strip().split()
		_map[_line[3]] = _line[2]
#chr - 0	scaffold00001_v1.0	0	1291680	0

with open(trackFl, 'r') as inFl:
	for line in inFl:
		_line = line.strip().split()
		_line[0] = _map[_line[0]]
		print('\t'.join(_line))
		
#scaffold00001_v1.0	0	99999	63.2241
