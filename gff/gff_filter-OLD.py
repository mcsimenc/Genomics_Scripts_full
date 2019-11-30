#!/usr/bin/env python3

import sys
import re

def help():
	print('''
	Usage:
	------------
	gff_filter.py <gff> [options]

	Description:
	------------
	Adapted from maker_filter_gff.py

	If multiple params are used they can override eachother. Dominance hierarchy:
	-scaf
	-id
	-pacid

	Options:
	------------
	-scaf <list>	Output scafs from the fasta in <list>

	-id <list>	Output features from gene models whose gene feature ID
			matches something in list.

	-pacid <list>	Same as id but uses pacid as identifier

	-v		Invert. Print non-matching lines.
	''')
	sys.exit(0)


args = sys.argv

if '-h' in args or '-help' in args or len(args) < 2:
	help()

if '-id' in args and '-pacid' in args:
	print('Use only one of -id, -pacid', file=sys.stderr)
	sys.exit()

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
					if '-v' in args:
						continue
					else:
						print(line, end='')
				else:
					if '-v' in args:
						print(line, end='')
					else:
						continue

	sys.exit()




if '-id' in args:
	IDpth = args[args.index('-id') + 1]
	IDset = set()

elif '-pacid' in args:
	IDpth = args[args.index('-pacid') + 1]
	IDset = set()

else:
	sys.exit()

with open(IDpth) as IDfl:
	for line in IDfl:
		IDset.add(line.strip())

with open(inflpth) as infl:
	for line in infl:
		if not line.startswith('#') and not line == '\t' and not line == '\r' and not line.startswith(' '):
			if line.split('\t')[2] == 'gene':
				# gene features don't have pacid in Physcomitrella v3.3
				if '-id' in args:
					ID_match = re.search('ID=(.+?)(?=;|$)', line)
				if '-pacid' in args:
					ID_match = re.search('ID=(.+?)(?=;|$)', line)
			elif line.split('\t')[2] == 'mRNA':
				if '-id' in args:
					ID_match = re.search('Parent=(.+?)(?=;|$)', line)
				elif '-pacid' in args:
					ID_match = re.search('pacid=(.+?)(?=;|$)', line)
			elif line.split('\t')[2] in ['exon', 'CDS', 'five_prime_UTR', 'three_prime_UTR']:
				if '-id' in args:
					ID_match = re.search('Parent=(.+?)(?=;|:|$|-mRNA)', line)
				elif '-pacid' in args:
					ID_match = re.search('pacid=(.+?)(?=;|$)', line)
			else:
				print('line not gene, mRNA, exon, CDS, or UTR?\t{0}'.format(line), end='', file=sys.stderr)
				if '-id' in args:
					ID_match = re.search('ID=(.+?)(?=;|$)', line)
				if '-pacid' in args:
					ID_match = re.search('ID=(.+?)(?=;|$)', line)
				#print(line, end='')
				#continue

			if ID_match.group(1) in IDset:
				if '-v' in args:
					continue
				else:
					print(line, end='')
			else:
				if '-v' in args:
					print(line, end='')
				else:
					continue
