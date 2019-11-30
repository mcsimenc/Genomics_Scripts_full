#!/usr/bin/env python3

import sys

total_length = 0
total_gc = 0

with open(sys.argv[1]) as fl:
	for line in fl:
		if not line.startswith('>'):
			total_length += len(line.strip())
			total_gc += len([ 1 for i in line.strip() if i in 'GC'])

print(total_gc/total_length)
