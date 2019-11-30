#!/usr/bin/env python3

import sys

genes = {}

for line in sys.stdin:

	contents = line.strip().split('\t')
	gene = contents[0]

	if gene in genes:
		for item in contents[1].split(','):
			genes[gene].add(item)
	else:
		genes[gene] = set(contents[1].split(','))




for gene in sorted(list(genes.keys())):
	print('{0}\t{1}'.format(gene, ','.join(sorted(list(genes[gene])))))
