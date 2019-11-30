#!/usr/bin/env python3

import sys

for line in sys.stdin:
	line = line.strip()
	if line.startswith('>'):
		line = '_'.join(line.split()[:2])
	print(line)
