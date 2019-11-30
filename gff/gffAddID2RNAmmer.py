#!/usr/bin/env python3

# RNAmmer's GFF output's attributes column is non-standard. This script adds the ID key and a unique 4-digit identifier for each entry in the 9th field.

import sys

counts = {}
for line in sys.stdin:
	if line.startswith('#'):
		#print(line, end='')
		continue

	line = line.strip().split('\t')
	feat = line[-1]
	if feat in counts:
		counts[feat] += 1
		feat = 'ID={0}_{1}'.format(feat, str(counts[feat]).zfill(4))
		line[-1] = feat
		print('\t'.join(line))
	else:
		counts[feat] = 1
		feat = 'ID={0}_{1}'.format(feat, str(counts[feat]).zfill(4))
		line[-1] = feat
		print('\t'.join(line))


