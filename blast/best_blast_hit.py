#!/usr/bin/env python3


# This script takes a blast output format 7 table on stdin and prints the first (presumably highest scoring/lowest evalue) hit for each query on stdout


import sys



last_query = '!@#$%^&*()_QWERTYUIOP{'
for line in sys.stdin:
	if not line.startswith('#') and not line.startswith('{0}\t'.format(last_query)):
		print(line, end='')
		last_query = line.strip().split()[0]

