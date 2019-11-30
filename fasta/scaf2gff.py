#!/usr/bin/env python3

import sys

for line in sys.stdin:

	scaf, length = line.strip().split()

	print('{0}\tmanual\tscaffold\t1\t{1}\t.\t.\t.\tID={0}'.format(scaf, length))
