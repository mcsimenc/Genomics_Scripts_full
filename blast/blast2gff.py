#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		blast2gff.py -blast <file> > <output.gff>

		Description:
		------------
		Converts command-line blast tabular output (format 6 or 7) to GFF3 format.
		Blast formats 6 and 7 can be customized so as to include subject strand.
		Subject strand is assumed to be the 13th field in the blast file (if included)

		Prints GFF3 to stdout.


		Options:
		------------
		-map	identifier map. e.g. for nt or nr. Before first space is identifier
			and after is description. see NCBI nt db example:
			X17276.1 Giant Panda satellite 1 DNA
		
		''')
	sys.exit(0)

args = sys.argv

if not '-blast' in args or len(args) < 3:
	help()

blast_fl_pth = args[args.index('-blast') + 1]

print('##gff-version 3')

source = "blastn"
type = "hit"
phase = "."
#last_feat = ""

idMap = {}
if '-map' in args:
	with open(args[args.index('-map') + 1]) as mapFl:
		for line in mapFl:
			item = line.strip().split(' ',1)
			idMap[item[0]]=item[1]

with open(blast_fl_pth) as blast_fl:
	for line in blast_fl:
		if line.startswith("#"):
			continue
		else:
			blast_line = line.strip().split()
		#	if last_feat == blast_line[0]:
		#		continue
		#	else:
		#		last_feat = blast_line[0] # so as to not use more that one HSP for each feature
			

			hit = blast_line[1]
			if '-map' in args:
				try:
					desc = idMap[hit]
					if ' ' in desc:
						desc = desc.replace(' ', '_')
					attr = "ID={0}_{1}".format(hit,desc)
				except KeyError:
					print('not_found_in_map_file:\t{0}'.format(hit))
			else:
				attr = "ID={0}".format(hit)
			seq_id = blast_line[0]
			start = int(blast_line[6])
			end = int(blast_line[7])
			score = blast_line[10]
			if start > end:
				print(start, end)
				start, end = end, start
				print(start, end)
				sys.exit()
			try:
				if blast_line[12] == "plus":
					strand = "+"
				elif blast_line[12] == "minus":
					strand = "-"
			except IndexError:
				strand = "."

			print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}".format(seq_id, source, type, start, end, score, strand, phase, attr))
