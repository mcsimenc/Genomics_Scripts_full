#!/usr/bin/env python3

import sys

args = sys.argv

if not len(args) == 3:

	print('''
		usage:
			NewRepeatModelerLibSeqHeaders.py [comma-sep list of filepaths] [comma-seplist of prefixes associated with fileheaders]

		example:

			NewRepeatModelerLibSeqHeaders.py file1.tab,file2.txt,file3.tbl repbase,dfam,pfam


		Input files are treated as if they are tab-delimited with two fields, the first
		being the key and the second being the value. It is assumed that keys are unique.
		A two-field tab-delimited file is output to stdout where the first field is the
		key and the second field is the new name, of the form:

			key__prefix1_value1__prefix2_value2__prefix3_value3

		''', file=sys.stderr)

	sys.exit()


in_flpaths = args[1].split(',')

prefixes = args[2].split(',')



dct = {}

for i in range(len(in_flpaths)):

	with open(in_flpaths[i]) as in_fl:

		for line in in_fl:

			key, val = line.strip().split('\t')

			if key in dct:

				dct[key] = '{0}__{1}_{2}'.format(dct[key], prefixes[i], val)

			else:

				dct[key] = '{0}__{1}_{2}'.format(key, prefixes[i], val)



for key in sorted(list(dct.keys())):

	print('{0}\t{1}'.format(key, dct[key]))
