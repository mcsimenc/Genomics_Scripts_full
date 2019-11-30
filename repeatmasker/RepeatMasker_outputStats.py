#!/usr/bin/env python3

import sys



def help():
	print('''
		Usage:
		------------
		RepeatMasker_outputStats.py < inputfile [options] > outputfile

		Description:
		------------
		Calculates various stats for RepeatMasker output (stdout table).

		Options:
		------------
		-c	Print final count (at end)
		-h	Display help
		-n	Print query names
		-p	Threshold for minimum proportion masked (default is 0.0)
		-pr	Print proportions

		''')
	sys.exit(0)

args = sys.argv

if len(args) == 1:
	help()

c = False
n = False
p = 0.0
pr = False

if '-h' in args or '-help' in args:
	help()
if '-c' in args:
	c = True
if '-n' in args:
	n = True
if '-p' in args:
	p = float(args[args.index('-p')+1])
if '-pr' in args:
	pr = True
	

queryPropMasked = {}
for line in sys.stdin:
	contents = line.strip().split()
	try:
		int(contents[0])
	except:
		continue

	start = float(contents[5])
	end = float(contents[6])
	left = float(contents[7][1:-1])

	try:
		queryPropMasked[contents[4]] += (end-start)/(end+left-1)
	except KeyError:
		queryPropMasked[contents[4]] = (end-start)/(end+left-1)


ct = 0
for query in queryPropMasked:
	proportion = queryPropMasked[query]
	if proportion >= p:

		ct += 1

		if n == True and pr == True:
			print('{0}\t{1}'.format(query,proportion))
		elif n == True:
			print(query)
		elif pr == True:
			print(proportion)

if c == True:
	print(ct)
