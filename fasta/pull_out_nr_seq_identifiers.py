#!/usr/bin/env python3

# This script takes a list of sequence identifiers on stdin and searches a fasta file (provided as the first argument) for sequence identifiers that match the ones given on stdin, printing those lines to stdout.

# USAGE:
# pull_out_nr_seq_identifiers.py <fasta_file> < sed_ids

import sys
import re

id_set = set()
for line in sys.stdin:
	id_set.add(line.strip())



id_pattern = re.compile('^>(.+?)\s')
with open(sys.argv[1]) as nr:
	for line in nr:
		if line.startswith('>'):
			current_id = re.match(id_pattern, line).group(1)
			if current_id in id_set:
				print(line, end='')
