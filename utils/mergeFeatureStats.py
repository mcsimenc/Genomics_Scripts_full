#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		mergeFeatureStats.py -features <list_of_feature_names> [-files file1,file2,file3...]

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


file_names = args[args.index('-files') +1 ].split(',')

if '-cbind' in args:
	data = {}
	for flname in file_names:
		line_num = 0
		with open(flname) as fl:
			for line in fl:
				line_num += 1
				if line_num in data:
					data[line_num] += '\t{0}'.format(line.strip())
				else:
					data[line_num] = line.strip()

	for key in data:
		print(data[key])

elif '-features' in args:
	headers = ['features_name']

	data = {}
	featlist = []
	# to store location(s) of features in dict 'data', because keys of 'data' are line numbers (to preserve original order of feat list when outputting)
	feat_locs = {}

	featflname = args[args.index('-features') + 1]

	feat_num = 0

	# add features as key in a dict to store other info from the files
	with open(featflname) as featfl:
		for line in featfl:
			feat_num += 1
			feature = line.strip()
			data[feat_num] = [feature]
			if feature in feat_locs:
				print("WARNING: Duplicate feature names in feature list:{0}".format(feature), file=sys.stderr)
				feat_locs[feature].append(feat_num)
			else:
				feat_locs[feature] = [feat_num]
		num_cols = 1


	# go through each file and save info for features from the feature list 
	for flname in file_names:

		headers.append(flname)

		with open(flname) as fl:

			num_cols += 1

			for line in fl:

				contents = line.strip().split('\t')
				featname = contents[0]

				if featname in feat_locs:
					for key in feat_locs[featname]:
						data[key].append(contents[1])

			# add periods to the dict for features not found
			for key in data:
				if len(data[key]) != num_cols:

					data[key].append('.')

	# print headers
	if '-nohead' not in args:
		print('\t'.join(headers))

	# print data
	for key in range(1, feat_num + 1):
		print ('\t'.join(data[key]))

else:
	help()
