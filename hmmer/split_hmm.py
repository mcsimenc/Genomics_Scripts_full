#!/usr/bin/env python3

# I think this script splits a multi-hmm file into individual ones with sequential integer names, i.e. 1.hmm, 2.hmm, 3.hmm, ...

import sys

num = 0

for line in sys.stdin:

	if not line.startswith('#'):

		if line.startswith('HMMER3/f'):

			num += 1

			with open('{0}.hmm'.format(num), 'w') as out_fl:

				out_fl.write(line)

		else:

			with open('{0}.hmm'.format(num), 'a') as out_fl:

				out_fl.write(line)
