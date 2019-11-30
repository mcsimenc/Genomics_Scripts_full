#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		modelnamemap_export.ann2uni.ann.py <uni.ann> <export.ann_seqnames>

		Description:
		------------
		Maps names from output of `fathom export uni.ann uni.dna` files to 
		names used in uni.ann and uni.dna.

		Prints two columns to stdout: (1) the name used for models in export.ann
		(should be the same as export.dna) derived from the single column file
		export.ann_seqnames (names like MODEL20229) and (2) the name used for models
		in uni.ann and uni.dna.
		
		''')
	sys.exit(0)


args = sys.argv

if len(args) != 3 or '-h' in args:
	help()

with open(args[1]) as unifl:

	with open(args[2]) as exportnamefl:

		export_seqnames = set(exportnamefl.read().split('\n'))
		already_printed_name = False
		uni_seqname = None

		for line in unifl:
			if line.startswith('>'):
				already_printed_name = False
				uni_seqname = line.strip()[1:]
			elif already_printed_name == True:
				continue
			elif line.strip().split('\t')[-1] in export_seqnames:
				print('{0}\t{1}'.format(line.strip().split('\t')[-1], uni_seqname))
				already_printed_name = True
