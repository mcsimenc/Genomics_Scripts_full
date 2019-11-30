#!/usr/bin/env python3

import sys
import re

def help():
	print('''
		Usage:
		------------
		fasta_stats.py [fasta_file] [options]

		Description:
		------------
		Count lengths of fasta sequences. This script is
		slow if run without -x. By default it doesn't count gaps (-)
		or stop codons (*).

		Options:
		------------
		-l Length. Determine length of sequences. Outputs
		   two columns, sequence name and sequence length.

		-h Help. Display this help.

		-s Subset. Get stats for only sequences whose name
		   is in a list. Usage: -s <seq_list>

		-t Get total length of all sequences in fasta

		-x Don't check characters, just count them.
		''')
	sys.exit(0)


# Get parameters
args = sys.argv

# If asked for help or insufficient parameters
if "help" in args or "h" in args or len(args) < 3:
	help()


# Check for input file
try:
	in_fl = open(args[1])
except FileNotFoundError:
	print('\nThe input file was not found.\n')
	sys.exit(1)


# Check for s flag and associated file
s = False

try:
	s_ind = args.index('-s')
	s_fl = open(args[s_ind + 1])
	s_lst = s_fl.read().splitlines()
	s = True
except ValueError:
	pass
except FileNotFoundError:
	print('\nThe sequence list file was not found\n')
	sys.exit(1)

dont_count_set = set('*-')

if '-l' in args or '-t' in args:
	name = ''
	count = False
	length = 0
	len_dct = {}
	total_length = 0
	for line in in_fl:
		if line.startswith('>'):
			if count == True:
				len_dct[name]=length
				name = ''
				length = 0

			count = False

			if s == True:
				name = line.strip()[1:]
				if name in s_lst:
					count = True
			if s == False:
				name = line.strip()[1:]
				count = True
		else:
			if '-x' in args:
				if count == True:
					total_length += len(line.strip())
					length += len(line.strip())
			else:
				if count == True:
					total_length += len([i for i in line.strip() if not i in dont_count_set])
					length += len([i for i in line.strip() if not i in dont_count_set])

		len_dct[name]=length

# Output
if '-t' in args:
	print(total_length)
	sys.exit()
if s == True:
	pass
else:
	s_lst = len_dct.keys()	
for name in s_lst:
	print(name + '\t' + str(len_dct[name]) + '\r')
