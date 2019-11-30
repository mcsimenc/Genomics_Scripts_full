#!/usr/bin/env python3

# takes 2-col tab-delimited input, outputs matrix of membership of second column items to first column items

import sys

annot_dct = {}

genes = set()

for line in sys.stdin:

	taxon, gene = line.strip().split('\t')

	genes.add(gene)

	if taxon in annot_dct:

		annot_dct[taxon][gene] = 1

	else:

		annot_dct[taxon] = {gene:1}

genes_sorted = sorted(list(genes))

for gene in genes_sorted:

	for taxon in annot_dct:

		if gene not in annot_dct[taxon]:

			annot_dct[taxon][gene] = 0


taxa = sorted(list(annot_dct.keys()))

print('\t{0}'.format('\t'.join(genes_sorted)), end='')

for taxon in taxa:

	print('\n{0}'.format(taxon), end='')

	for gene in genes_sorted:

		print('\t{0}'.format(annot_dct[taxon][gene]), end='')

	#print('\n')
