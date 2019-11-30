#!/usr/bin/env python3

import sys
import re

def help():
	print('''
		Usage:
		------------
		bed2stats.py -f <bedfile> -types type1[,type2[,type3[,...]]]

		Description:
		------------
		Summarizes information from input file for features given by
		-types.
		

		Options:
		------------
		-f		Input file.
		
		-types		Comma-separated list of types to summarize info

		''')
	sys.exit(0)


args = sys.argv

inverse = False
if '-v' in args:
	inverse = True

if "-help" in args or "-h" in args or len(args) < 5 or '-f' not in args or '-types' not in args:
	help()


inflname = args[args.index('-f') + 1]

if '-types' in args:
	types = args[args.index('-types') + 1].split(',')
else:
	types = []


repeats = {}
shrt_repeats = {}
featlens = {t:0 for t in types}
with open(inflname) as infl:

	for line in infl:
		contents = line.strip().split()
		t = contents[7]
		if t in types:
			start = int(contents[1])
			end = int(contents[2])
			length = abs(end-start)
			featlens[t] += length



			if t == 'match':

				id = re.search('Name=species:(.+);', line).group(1)
				genus = re.search('genus:(.+)', id).group(1)
				species = re.search('(^.+)\|', id).group(1)

				try:
					repeats[genus][0].append(species)
					repeats[genus][1].append(length)
				except KeyError:
					repeats[genus] = [ [species], [length] ]

kinds = ['Retrotransposon', 'DNA', 'LINE', 'SINE', 'Other', 'LTR', 'Satellite', 'Low_complexity', 'ARTEFACT', 'Unspecified', 'tRNA', 'rRNA', 'Simple_repeat', 'RC', 'snRNA']

for genus in repeats:

	data_added = False

	for group in kinds:

		if genus.startswith(group):

			try:
				shrt_repeats[group][0] = shrt_repeats[group][0] + repeats[genus][0]
				shrt_repeats[group][1] = shrt_repeats[group][1] + repeats[genus][1]
			except KeyError:
				shrt_repeats[group] = [ repeats[genus][0], repeats[genus][1] ]

			data_added = True

			break

	if data_added == False:

		try:
			shrt_repeats[genus][0] = shrt_repeats[genus][0] + repeats[genus][0]
			shrt_repeats[genus][1] = shrt_repeats[genus][1] + repeats[genus][1]
		except KeyError:
			shrt_repeats[genus] = [ repeats[genus][0], repeats[genus][1] ]

shrt_repeats_types = sorted(list(shrt_repeats.keys()))
full_repeats_types = sorted(list(repeats.keys()))


for t in types:
	print('{0}\t{1}'.format(t, str(featlens[t])))

for t in shrt_repeats_types:
	print('{0}\t{1}'.format(t, str(sum(shrt_repeats[t][1]))))
