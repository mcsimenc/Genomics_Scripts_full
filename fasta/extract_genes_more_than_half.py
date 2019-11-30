#!/usr/bin/env python3

import re
import sys

args = sys.argv

if len(args) != 4:

	print('''
		usage:
			extract_genes_more_than_half.py <list> <fasta> <out_prefix>


		writes fasta files for each gene that is in more than half the taxa


		<list>	a two col list where first col is taxon and second col is gene name

		<fasta>	fasta file that has gene name in seq headers

		<out_prefix>	output will be written like: <out_prefix>.<gene_name>.fasta

		''',file=sys.stderr)

	sys.exit()




taxon_counts = {}

taxa = set()

with open(args[1]) as in_fl:

	for line in in_fl:

		taxon, gene = line.strip().split('\t')

		short_gene = gene.split('_')[0]

		taxa.add(taxon)

		if short_gene in taxon_counts:

			taxon_counts[short_gene].add(taxon)

		else:

			taxon_counts[short_gene] = set([taxon])


half_taxa = len(taxa) / 2 # for selecting genes present in more than half of the taxa

#half_taxa = 0 # for selecting all genes

to_write = []

for gene in taxon_counts:

	if len(taxon_counts[gene]) > half_taxa:

		to_write.append(gene)


out_prefix = sys.argv[3]

with open('{0}.info.txt'.format(out_prefix), 'w') as out_fl:

	out_fl.write('# Half_taxa:{0}\n'.format(half_taxa))

	out_fl.write('Gene\tnum_taxa\n')

	for gene in to_write:

		out_fl.write('{0}\t{1}\n'.format(gene, len(taxon_counts[gene])))



for gene in to_write:

	with open('{0}.{1}.fasta'.format(out_prefix, gene), 'w') as out_fasta_fl:

		with open(args[2]) as in_fasta_fl:

			WRITE = False

			for line in in_fasta_fl:

				if line.startswith('>'):

					if re.search('_{0}$|_{0}_'.format(gene), line) != None:

						WRITE = True

						out_fasta_fl.write(line)

					else:

						WRITE = False

				else:

					if WRITE:

						out_fasta_fl.write(line)
