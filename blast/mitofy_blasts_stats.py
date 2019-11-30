#!/usr/bin/env python3

import sys
import re
from subprocess import check_output


def help():
	print('''
		Usage:
		------------
		python3 ./blasts_stats.py [dir] [options]

		Description:
		------------
		This script was written specifically for obtaining information from
		the *.blastn and *.blastx files output by Mitofy.

		Finds all files with an extension of .*blast* while recursing through
		the directory [dir] and writes a summary of certain information contained
		within in the following tab-delimited format:

		Column 1: Input sequence (sequence to be annotated by Mitofy)
		Column 2: Number of unique proteins matching
		Column 3: Unique matching proteins

		Options:
		------------
		-c Min unique hit count for sequence outputs

		-E Max tolerated Expect value. Default is E_val=1e-10

		-h Show this help
	
		-n Output input sequence name only

		Example call:
		------------
		python3 blasts_stats.py ~/data/mitofy_output/ -E 1e-6 -c 10 -n
		''')
	sys.exit(0)


args = sys.argv

if not len(args) > 1:
	help()


opts = ''.join(args[2:])

if 'h' in opts or 'help' in opts:
	help()


search_dir = args[1]

# Parse E-value
try:
	Epat = re.compile('(?<=E)[0-9]+e*-[0-9]*')
	Ematch = Epat.search(opts)
	E_val = float(Ematch.string[Ematch.start():Ematch.end()])
except:
	E_val = 1e-10


# Parse -c threshold
try:
	cpat = re.compile('(?<=c)[0-9]+')
	cmatch = cpat.search(opts)
	c_val = int(cmatch.string[cmatch.start():cmatch.end()])
except:
	c_val = 0

# Get name-only option status
name_only = False

if 'n' in opts:
	name_only = True



# Get paths to all BLAST output files in all subdirectories
blast_files = check_output('find ' + search_dir + ' -name "*blast*"', shell=True).decode().split('\n')[1:-1]

# Dictionary to hold seq name, hit counts, and hit IDs
summary = {}

# Go through each blast file and extract information.
# The main idea is to check hit E values and if they are
for fl in blast_files:

	current_fl = open(fl, 'r')
	db = ''
	in_seq = ''
	skip_line = False
	count_hits = False
	
	for line in current_fl:

		if line.startswith('>'):
			break

		if line.strip() == '':
			continue

		if skip_line == True:
			skip_line = False
			count_hits = True
			continue

		if count_hits == True:
			if float(line.strip().split(' ')[-1]) <= E_val:
				summary[in_seq][0] += 1
				summary[in_seq][1].add(db)
				break

		if line.startswith('Database'):
			db = line.strip().split(' ')[-1].split('/')[-1]

		if line.startswith('Query'):
			in_seq = line.strip()[7:]
			try:
				summary[in_seq][0]
			except:
				summary[in_seq] = [0,set()]

		if line.startswith('Sequences'):
			skip_line = True


summary_lst = []
for seq_name in summary:
	summary_lst.append((seq_name, summary[seq_name][0], ','.join(list(summary[seq_name][1]))))

summary_lst.sort(key=lambda x: x[1])


if name_only == True:
	for data in summary_lst:
		if data[1] >= c_val:
			print(data[0] + '\r')
sys.exit(0)



for data in summary_lst:
	if data[1] >= c_val:
		print(data[0] + '\t' + str(data[1]) + '\t' + data[2] + '\r')
