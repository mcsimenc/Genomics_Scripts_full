#!/usr/bin/env python3

# this script takes a gff on stdin and prints to stdout a protein fasta for lines that match the attribute aa_seq=
# the seq header is the ID attributes value and the sequence is the aa_seq attributes value

import sys
import re

aa_pat = re.compile('aa_seq=(.+?);')
id_pat = re.compile('ID=(.+?);')

for line in sys.stdin:
	try:
		aa_seq = re.search(aa_pat, line).group(1)
		header = re.search(id_pat, line).group(1)
		print('>{0}'.format(header))
		print(aa_seq)
	except:
		pass
