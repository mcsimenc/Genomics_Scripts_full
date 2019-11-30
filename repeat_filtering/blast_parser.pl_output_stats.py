#!/usr/bin/env python3

import sys
import re


def help():
	print('''
		Usage:
		------------
		blast_parser.pl_output_stats.py < inputfile [options] > outputfile

		Description:
		------------
		Gets stats on HSP alignments from blast_parser.pl-converted file.

		Options:
		------------
		-c	[int] Ceiling for proportion overlab. Output sbj or query names for which the percentage of
			the query that is part of the HSP is less than or equal to this value.

		-f	[int] Floor for proportion overlab. Output sbj or query names for which the percentage of
			the query that is part of the HSP is greater or equal to than this value.

		-l	Use longest HSP calculated as query alignment range. Incompatible with -s
		-s	Use highest scoring HSP. Incompatible with -l
		-sbj	Output subject names. Incompatible with -% and -sbjq
		-sbjq	Output subject names in col 1 and query names in col 2. Incompatible with -% and -sbj
		-%	Output format is 2 columns: query names and % query matched by best (see options) HSP.

		''') 

	sys.exit(0)


args = sys.argv

if '-h' in args or '-help' in args or len(args) < 2:
	help()

if '-l' in args and '-s' in args:
	help()

if '-sbj' in args and '-sbjq' in args:
	help()


# Set ceiling cutoff
try:
	ceiling = float(args[args.index('-c') + 1])
except ValueError:
	ceiling = 100.0

# Set floor cutoff
try:
	floor = float(args[args.index('-f') + 1])
except ValueError:
	floor = 0.0

# stats will have the format: { queryname:[ [ querylength, sbj1len, sbj2len, sbj3len, ... ], [queryname, sbj1name, sbj2name, sbj3name, ...] ] }
stats = {}
	
query_pattern = re.compile('(.+)\s\((\d+)\)')
query_alignment_length_pattern = re.compile('\s(\d+\.\.\d+)\s')
subject_name_pattern = re.compile('(\S+)\s')
next_query = False
hit_name_line = False
hit_length_line = False
query_name = ''
subject_name = None

for line in sys.stdin:

	# Note that the next line has the query name.
	if line.strip() == '':
		next_query = True
		hit_name_line = False
		continue

	# This is true after a blank line
	elif next_query == True:
		next_query = False
		# Get the query name
		query_name = re.search(query_pattern, line.strip()).group(1)
		# Get the query length
		query_length = float(re.search(query_pattern, line.strip()).group(2))

		# Add the query name and length to the dictionary stats
		try:
			stats[query_name]
			#sys.exit('Duplicate query name: {0}'.format(query_name))
			print('Duplicate query name: {0}'.format(query_name), file=sys.stderr)

		except KeyError:
			stats[query_name] = [ [query_length], [query_name] ]

	else:
		# If this pattern matches then we're on the subject alignment details line, occurring one line below the name line.
		try:
			# Get subject length
			query_align_range = re.search(query_alignment_length_pattern, line.strip()).group(1)
			query_align_range = [int(i) for i in query_align_range.split('..')]

			# Calculate alignment length. Add 1 to avoid off by one error
			query_align_length = query_align_range[1]-query_align_range[0] + 1
			stats[query_name][0].append(query_align_length)
			stats[query_name][1].append(subject_name)

		# If the top pattern doesn't match then we're on the subject name line
		except AttributeError:
			subject_name = re.search(subject_name_pattern, line.strip()).group(1)
			continue

# Highest scoring HSP
if '-s' in args:

	if '-%' in args:
		for query in stats:
			query_align_percent = (stats[query][0][1]/stats[query][0][0])*100.0
			if query_align_percent <= ceiling and query_align_percent >= floor:
				print('{0}\t{1}\r'.format(query,float(query_align_percent)))

	elif '-sbj' in args:
		for query in stats:
			query_align_percent = (stats[query][0][1]/stats[query][0][0])*100.0
			if query_align_percent <= ceiling and query_align_percent >= floor:
				print('{0}\r'.format(stats[query][1][0]))

	elif '-sbjq' in args:
		for query in stats:
			query_align_percent = (stats[query][0][1]/stats[query][0][0])*100.0
			HSP_sbj_name = stats[query][1][1]
			if query_align_percent <= ceiling and query_align_percent >= floor:
				print('{0}\t{1}\t{2}\r'.format(HSP_sbj_name, query, query_align_percent))
			

# Longest HSP
if '-l' in args:
	if '-%' in args:
		for query in stats:
			longest_index = stats[query][0][1:].index(max(stats[query][0][1:]))
			longest_HSP_len = stats[query][0][1:][ longest_index ]
			longest_HSP_name = stats[query][1][1:][ longest_index ]
			query_align_percent = (longest_HSP_len/stats[query][0][0])*100.0
			if query_align_percent <= ceiling and query_align_percent >= floor:
				print('{0}\t{1}\r'.format(query,float(query_align_percent)))

	elif '-sbj' in args:
		for query in stats:
			longest_index = stats[query][0][1:].index(max(stats[query][0][1:]))
			longest_HSP_len = stats[query][0][1:][ longest_index ]
			longest_HSP_name = stats[query][1][1:][ longest_index ]
			query_align_percent = (longest_HSP_len/stats[query][0][0])*100.0
			if query_align_percent <= ceiling and query_align_percent >= floor:
				print('{0}\t{1}\r'.format(longest_HSP_name, query_align_percent))

	elif '-sbjq' in args:
		for query in stats:
			longest_index = stats[query][0][1:].index(max(stats[query][0][1:]))
			longest_HSP_len = stats[query][0][1:][ longest_index ]
			longest_HSP_name = stats[query][1][1:][ longest_index ]
			query_align_percent = (longest_HSP_len/stats[query][0][0])*100.0
			if query_align_percent <= ceiling and query_align_percent >= floor:
				print('{0}\t{1}\t{2}\r'.format(longest_HSP_name, query, query_align_percent))
