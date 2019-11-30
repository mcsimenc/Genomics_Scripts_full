#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		selectLowestAED.py -cols < <inputfile>

		Description:
		------------
		Takes a list of feature names, extracts information from files and outputs information
		from all files in one line for a given feature.

		Output:
		------------
		Prints to stdout tab-delimited with first column being the feature name and
		subsequent columns being the other information. A period is output if no data
		is found for a given feature in a given file. A tab-delimited header with the
		file names is output first.


		Options:
		------------
		-features	A list of feature names.

		-file		Comma-separated list of files consisting of two columns with the
				feature name in the first column.

		-cbind		Simply merge the files together, line for line. Files must be same length.

		-nohead		Suppress outputting headers.
		
		''')
	sys.exit(0)


args = sys.argv

if '-h' in args or len(args) < 4 or '-files' not in args:
	help()
