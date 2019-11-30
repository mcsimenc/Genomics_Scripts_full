#!/usr/bin/env python3

import sys

def help():
	print('''
 Usage:
 ------------
 getsubset.tsv.py -list <file> -file <file> [-char <ending char>]
 
 Description:
 ------------
 Match -file [-col] to -list
 Extracts lines from -file where column -col matches something in -list
 
 Options:
 ------------
 -char		Character that marks the end of the name in <file>. For example
 		-char -exon would allow for matching "gene-1-1-exon2". Default is a tab
 -col <int>	Default 1.
''')
	sys.exit(0)


args = sys.argv

if len(args) < 5:
	help()

lst_flpth = args[args.index('-list')+1]
fl_flpth = args[args.index('-file')+1]

if '-char' in args:
	char = args[args.index('-char')+1]
else:
	 char = None
if '-col' in args:
	col = int(args[args.index('-col')+1])
else:
	 col = 1

lst_subset = set()
with open(lst_flpth) as lstfl:
	for line in lstfl:
		lst_subset.add(line.strip())

with open(fl_flpth) as fl:
	for line in fl:
		dat = line.split()[col-1]
		if char != None:
			dat = dat.split(char)[col-1]
		if dat in lst_subset:
			print(line, end='')
