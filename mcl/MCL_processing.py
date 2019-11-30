#!/usr/bin/env python3

import sys
import re

def help():
	print('''
		Usage:
		------------
		MCL_processing.py [options] < out.MCL

		Description:
		------------
		Do things with MCL-edge output files.

		Options:
		------------
		-debug		Run extra code that will check for errors.

		-ltr_check	Print Left and right LTR names if they are in multiple clusters
				or are in different clusters.

				LTRs are expected to occur in pairs and left and right LTR names
				are expected to be the same except for a suffix of _0 or _1.

		-h		Help. Display this help.
		''')
	sys.exit(0)



args = sys.argv # Get parameters

# If asked for help or insufficient parameters
if "-help" in args or "-h" in args:
	help()




clusters = {} # put clusters in dict with cluster# as key and values are sets of names
LTR_names = set()

cluster_num = 0 # count clusters as reading in file
for line in sys.stdin:
	clusters[cluster_num] = set(line.strip().split('\t'))
	for name in clusters[cluster_num]:
		LTR_names.add(name)
	cluster_num += 1

LTR_names = sorted(list(LTR_names))


if '-ltr_check' in sys.argv:

	LTR_pairs = {} # put LTR pairs in LTR dict
	val = 0
	count = 0
	strip_pat = re.compile('_\d.*$')

	#tmp var
	#print_check = 0
	singlets = set()
	for name in LTR_names:
		if count%2 == 1:
			# check that both LTRs here have the same name prefix
			ltr_name_1 = re.sub(strip_pat,'',LTR_pairs[val][0])
			ltr_name_2 = re.sub(strip_pat,'',name)
			if ltr_name_1 != ltr_name_2:
				# singlets.add(LTR_pairs[val][0]) # check with final singlets from dict
				val += 1 # put this ltr with a new key in LTR_pairs but don't increment count so this block runs again
				LTR_pairs[val] = [name]
			else:
				LTR_pairs[val].append(name)
				val += 1
				count += 1
		else:
			LTR_pairs[val] = [name]
			count += 1

	for pair in LTR_pairs:
		if len(LTR_pairs[pair]) == 2:
			L = LTR_pairs[pair][0]
			R = LTR_pairs[pair][1]
			L_clusters = []
			R_clusters = []
			for clust in clusters:
				if L in clusters[clust]:
					L_clusters.append(clust)
				if R in clusters[clust]:
					R_clusters.append(clust)
		if L_clusters !=  R_clusters or (len(L_clusters) > 1 or len(R_clusters) > 1):
			print(L, L_clusters)
			print(R, R_clusters)
			print('- - - - - - - - - - - - - - - - -')

	if '-debug' in sys.argv:

		# check that all singlets in dict are actually singlets in cluster input
		for pair in LTR_pairs:
			if len(LTR_pairs[pair]) == 1:
				ltr_prefix = re.sub(strip_pat,'',LTR_pairs[pair][0])
				copies = 0
				for name in LTR_names:
					if ltr_prefix == re.sub(strip_pat,'',name):
						copies += 1
				if copies > 1:
					print('THERE IS PROBABLY A BUG IN THE CODE: LTR NAME MADE INTO A DICTIONARY AS A SINGLET BUT IS NOT ACTUALLY A SINGLET IN INPUT FILE. CHECK HOW MANY COPIES OF:')
					print(ltr_prefix)
		 


c = 0
for name in LTR_pairs:
	print(LTR_pairs[name])
	c += 1
	if c > 30:
		break
