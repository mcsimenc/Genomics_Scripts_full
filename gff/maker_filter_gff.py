#!/usr/bin/env python3

import sys
import re

def help():
	print('''
		Usage:
		------------
		maker_filter_gff.py <maker.gff> [options]

		Description:
		------------
		Removes lines from a fasta based on options and prints the rest to stdout.

		Only use one option at a time! If both are used then only -scaf will be processed.

		Options:
		------------
		-scaf <list>		Remove scafs from the fasta in <list>

		-ID <list>		Removes features matching names in <list>
		
		''')
	sys.exit(0)


args = sys.argv

if '-h' in args or '-help' in args or len(args) < 2:
	help()

inflpth = args[1]

if '-scaf' in args:
	scfpth = args[args.index('-scaf') + 1]
	scfset = set()
	with open(scfpth) as scffl:
		for line in scffl:
			scfset.add(line.strip())

	with open(inflpth) as infl:
		for line in infl:
			if not line.startswith('#'):
				if line.split('\t')[0] in scfset:
					continue
				else:
					print(line, end='')

	sys.exit()




if '-ID' in args:
	IDpth = args[args.index('-ID') + 1]
	IDset = set()
	with open(IDpth) as IDfl:
		for line in IDfl:
			IDset.add(line.strip())

	with open(inflpth) as infl:
		for line in infl:
			if not line.startswith('#'):
				if line.split('\t')[2] == 'gene':
					ID_match = re.search('ID=(.+);', line)
				elif line.split('\t')[2] == 'mRNA':
					ID_match = re.search('ID=(.+?)-mRNA-1;', line)
				elif line.split('\t')[2] in ['exon', 'CDS', 'five_prime_UTR', 'three_prime_UTR']:
					ID_match = re.search('ID=(.+?)-mRNA-1:', line)
				else:
					print('line not gene, mRNA, exon, CDS, or UTR?\t{0}'.format(line), end='', file=sys.stderr)
					print(line, end='')
					continue

				if ID_match.group(1) in IDset:
					continue
				else:
					print(line, end='')
