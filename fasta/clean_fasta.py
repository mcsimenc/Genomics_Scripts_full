#!/usr/bin/env python3

# this script will replace 'x' or 'X' with 'N' in the sequence and add a number to the end of duplicate seqids to fix these problems that will prevent makeblastdb from making a db.

import sys

headers = {}

for line in sys.stdin:

	line = line.strip()

	if line.startswith('>'):

		if line in headers:

			headers[line] += 1
			line = '{0}_{1}'.format(line, headers[line])

			print(line)

		else:

			headers[line] = 0
			print(line)

	else:

		if 'x' in line:

			line = line.replace('x','n')

		if 'X' in line:

			line = line.replace('X','N')

		print(line)
