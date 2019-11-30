#!/usr/bin/env python3

import sys

# This script takes a two column file as input on stdin
# it's assumed that the first column is the name of a feature
# and the second column is a component of that feature
# and that components for a given feature are in order such that a compenent at row n is before the component at row n+1
# it combines components for a given feature and counts how many times components in that order appear
# that's it

# Edit: I think this is for creating a list of domains for each feature from LTRDigest output...

d = {}
counts = {}

for line in sys.stdin:
	contents = line.split()
	ltrname = contents[0]
	domain = contents[1]
	if ltrname in d:
		d[ltrname].append(domain)
	else:
		d[ltrname] = [domain]

for ltr in d:
	ltr = tuple(d[ltr])
	if ltr in counts:
		counts[ltr] += 1
	else:
		counts[ltr] = 1

for ltrtype in counts:
	print('{0}\t{1}'.format(counts[ltrtype], ',  '.join(ltrtype)))
