#!/usr/bin/env python3

import sys
import re

def help():
	print('''
		Usage:
		------------
		python3 ./count_hits.py [input_file] [col_num] [options]

		Description:
		------------
		This script will output two columns, the first
		containing unique values from the column of the
		tab-delimited input file specified by [col_num],
		(must be an integer) and the second containing the
		number of times that value occurred in the input
		file.

		Options:
		------------
		-c [int] Output only values occuring >= [int] times

		###-d	Column delimmiter. Default is a space 

		-n	Output only one column, containing the name

		''')
	sys.exit(0)

args = sys.argv


if 'help' in args or 'h' in args or not len(args) > 2:
	help()


# Process from command line input
try:
	opts = ''.join(args[3:])
except:
	pass

try:
	cpat = re.compile("(?<=c)[0-9]*")
	cval = cpat.search(opts)
	c = int(cval.string[cval.start():cval.end()])
except:
	c = 1

if "n" in opts:
	n = 1
else:
	n=0

# Get -d option
#if "-d" in args:
#	delim = args[args.index("-d") + 1]
#else:
#	delim = " "
delim = "\t"

try:
	col = int(args[2])
except ValueError:
	help()

# Extract column values and count

infl = open(args[1])
ct_dct = {}

for line in infl:
	contents = line.strip().split(delim)[col-1]
	try:
		ct_dct[contents] += 1
	except KeyError:
		ct_dct[contents] = 1	

ct_lst = []

for key in ct_dct:
	ct_lst.append((key,ct_dct[key]))

ct_lst.sort(key=lambda x: x[1],reverse=True)


if n == 0:
	for item in ct_lst:
		if item[1] < c:
			sys.exit(0)
		print(item[0]+'\t'+str(item[1]))
if n == 1:
	for item in ct_lst:
		if item[1] < c:
			sys.exit(0)
		print(item[0])
