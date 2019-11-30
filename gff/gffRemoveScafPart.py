#!/usr/bin/env python3

import sys

def help():
	print('''
	Usage:
	------------
	gffRemoveScafPart.py -scaf <str> -range <int-int> < input.gff > output.gff

	Description:
	------------
	Removes parts of scaffold specified. If a feature spans the end or start of the
	range it is removed.


	Options:
	------------
	-scaf <string>		Scaffold to remove

	-range <int-int>	Range to remove, e.g. -range 452-1823

	-h			Help

	''')
	sys.exit(0)


args = sys.argv

if '-h' in args or '-help' in args or len(args) < 5:
	help()

scafTarget = args[args.index('-scaf')+1]
r = args[args.index('-range')+1].split('-')
startTarget = int(r[0])
endTarget = int(r[1])

for line in sys.stdin:
	if not line.startswith('#'):

		contents = line.strip().split('\t')
		scaf = contents[0]
		if scaf == scafTarget:
			start = int(contents[3])
			end = int(contents[4])
			if (start >= startTarget and start < endTarget) or (end > startTarget and end < endTarget):
				continue
			else:
				print(line, end='')

		else:
			print(line, end='')
