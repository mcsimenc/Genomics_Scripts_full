#!/usr/bin/env python3

import sys

prevID = ''
for line in sys.stdin:
	if not line.startswith('#'):
		contents=line.strip().split("\t")
		ID = contents[-1].split('=')[1]
		with open('{0}.gff'.format(ID), 'a') as outfl:
			outfl.write(line)
