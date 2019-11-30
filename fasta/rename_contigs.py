#!/usr/bin/env python3

# I think this script renames fasta headers as sequential integers, i.e. >1, >2, >3, ...

import sys

i = sys.argv[0]
o = sys.argv[1]

with open(o, 'w') as out:
	with open(i) as fl:
		ct = 0
		for line in fl:
			if line.startswith('>'):
				out.write('>{0}\n'.format(str(ct)))
				ct += 1
			else:
				out.write(line)
