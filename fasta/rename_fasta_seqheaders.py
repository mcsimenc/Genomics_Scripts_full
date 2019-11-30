#!/usr/bin/env python3

import sys

args = sys.argv

if not len(args) == 3:

	print('''
		usage:
			rename_fasta_seqheaders.py <fasta> <map>



		Renames seq headers in fasta file according to mapping provided as <map>
		Written specifically for Josh's Santalales CP genome assemblies:
		If new name in mapping is pbs12_Mixo the new name output will be pbs12

		<map>
			a two-column file where first col is the old name and second col is new name

		''', file=sys.stderr)

	sys.exit()

map_dct = {}

genes_found = {}

# read in mapping
with open(args[2]) as in_fl:

	for line in in_fl:

		old, new = line.strip().split('\t')

		taxon = old.split('_')[0].split('-')[1]

		gene = new.split('_')[0]

		if taxon in genes_found:

			if gene in genes_found[taxon]:

				genes_found[taxon][gene] += 1

			else:

				genes_found[taxon][gene] = 1

		else:

			genes_found[taxon] = {gene:1}


		new = ('{0}_{1}'.format(taxon, gene), genes_found[taxon][gene]) # special code for maker santalales output

		map_dct[old] = new

#for g in genes_found:
#	print('{0}\t{1}'.format(g, ','.join([ gene for gene in genes_found[g] ])))
# read and alter fasta file, print to stdout
with open(args[1]) as in_fl:

	for line in in_fl:

		if line.startswith('>'):

			old = line.strip().lstrip('>')

			try:

				gene = map_dct[old][0].split('_')[1]

				gene_num = map_dct[old][1]

				taxon = old.split('_')[0].split('-')[1]

				if genes_found[taxon][gene] > 1:

					new = '>{0}_{1}_{2}'.format(taxon, gene, gene_num)

				else:

					new = '>{0}_{1}'.format(taxon, gene)


				print(new)

			except KeyError:

				print('NOT_FOUND_IN_MAPPING_FILE\t{0}'.format(old), file=sys.stderr)
				print(line, end='')

		else:

			print(line, end='')
