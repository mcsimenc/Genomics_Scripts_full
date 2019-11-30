#!/usr/bin/env python3

import sys

if len(sys.argv) == 1:
	print('''
	usage:
		removeNonLTRs.py <ltrs.list> < <multi.hmm>
	
	description:
		reads ltrs.list and then outputs HMMs from multi.hmm if Name of HMM is in ltrs.list
		''')
	sys.exit()

LTRs = set()
with open(sys.argv[1]) as listFl:
	for line in listFl:
		LTRs.add(line.strip())

PRINT = False
lines = ''
for line in sys.stdin:
	lines += line
	if line.startswith('//'):
		if PRINT:
			print(lines, end='')
			PRINT = False
		lines = ''

	elif line.startswith('NAME'):
		name = line.strip().split(' ')[-1]
		if name in LTRs:
			PRINT = True
		else:
			PRINT = False
