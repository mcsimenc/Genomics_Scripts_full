#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		subtract_columns.py <file> <col1> <col2>

		Description:
		------------
		Subtracts values in col2 from those in col1 and prints
		to stdout.

		''')
	sys.exit(0)

col1 = int(sys.argv[2])
col2 = int(sys.argv[3])

with open(sys.argv[1]) as infl:
	for line in infl:
		contents=line.split()
		
