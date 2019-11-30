#!/usr/bin/env python3

# usage:
#	annot2columns.py < Dfam.annotations

import sys
import re

print('Name\tDescription\tType')

name_pat = re.compile('NAME\s+(.+)')
desc_pat = re.compile('CT\s+Type;\s+(.+);')
type_pat = re.compile('CC\s+Type:(.+)')

out_line = ''

for line in sys.stdin:
	if line.startswith('#'):
		continue

	if line.startswith('NAME'):

		out_line += re.search(name_pat, line.strip()).group(1)

	elif line.startswith('CT'):

		out_line += '\t'

		out_line += re.search(desc_pat, line.strip()).group(1)

	elif line.startswith('CC'):

		out_line += '\t'

		out_line += re.search(type_pat, line.strip()).group(1)

		print(out_line)

		out_line = ''



# Dfam.annotations format. Made by this grep:
# grep -P '^NAME|^CC\s+Type|^CT\s+Type' Dfam.hmm > Dfam.annotations

#NAME  4.5SRNA
#CT    Type; ncNRA Gene;
#CC         Type: scRNA
#NAME  5S
#CT    Type; ncRNA Gene;
#CC         Type: rRNA
#NAME  5S_DM
#CT    Type; ncNRA Gene;
#CC         Type: RNA
#NAME  7SK
