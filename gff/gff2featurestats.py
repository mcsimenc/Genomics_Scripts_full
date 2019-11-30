#!/usr/bin/env python3

import os
import sys
import subprocess
import re

#qsub_stdout = subprocess.check_output('qsub {0}{1}.qsub'.format(self.output_dir, self.opt_dct['name']), shell=True)

#subprocess.call('maker2zff -n {0}*all.gff'.format(self.output_dir), cwd=self.output_dir, shell=True)


def help():
	print('''
		# ADAPTED FROM maker_gff2genomestats.py

		Usage:
		------------
		gff2featurestats.py -f <gff> -p <prefix> 

		Description:
		------------
		This script expects a nested format with gene first and its subordinate features after.
		Input a GFF3 file, outputs files with stats for features:

		1.	<prefix>.exon_length
		2.	<prefix>.intron_length
		3.	<prefix>.gene_length
		4.	<prefix>.exon_count


		Required parameters:
		------------
		-f	Path to input maker gff3 file (mandatory).

		-p	Output files prefix.
''')

#		-s	Assembly size in bases.
#			Salvinia cucullata first assembly: 222099292
#			Salvinia cucullata v1: 225872744
#			Salvinia cucullata v1.1: 232832424
#			Azolla filiculoides (celera asm, quivered): 692828876
#		''')

args = sys.argv

if '-h' in args:
	help()
	sys.exit()

try:
	gff = args[args.index('-f') + 1]
	out_prefix = args[args.index('-p') + 1]
	#genome_size = int(args[args.index('-s') +1])
except:
	help()
	sys.exit()


genes = {}
mrnas = {}
total_genic_length = 0
id = ''
mrna_id = ''

with open(gff, 'r') as gff_fl:

	for line in gff_fl:
		if line.startswith('#'):
			continue
		else:


			# Get gene lengths
			contents = line.strip().split()

			if contents[2].startswith('gene'):

				id = re.search('ID=(.+?)(?=;|$)', line).group(1)
				start = int(re.search('\sgene\s(\d+)\s', line).group(1))
				end = int(re.search('\d+\s(\d+)\s', line).group(1))
				length = end - start +1
				total_genic_length += length
				genes[id] = [(start,end),length]

			elif contents[2].startswith('mRNA'):
				mrna_id = re.search('ID=(.+?)(?=;|$)', line).group(1)
				start = int(re.search('\smRNA\s(\d+)\s', line).group(1))
				end = int(re.search('\d+\s(\d+)\s', line).group(1))
				length = end - start +1

				try:
					mrnas[mrna_id][0] = (start,end)
				except KeyError:
					mrnas[mrna_id] = [(start,end),[]]

			elif contents[2].startswith('exon'):

				mrna_id = re.search('ID=(.+?)(?=;|$|:)', line).group(1)
				#if not exon_id.startswith(mrna_id):
				#	print('GFF3 not sorted properly! This script expects a nested format with gene first and its subordinate features after', file=sys.stderr)
				start = int(re.search('\sexon\s(\d+)\s', line).group(1))
				end = int(re.search('\d+\s(\d+)\s', line).group(1))
				length = end - start +1

				try:
					mrnas[mrna_id][1].append((start,end))
				except KeyError:
					mrnas[mrna_id] = ['', [(start,end)]]


			#elif contents[2].startswith('CDS'):

			#	cds_id = re.search('ID=(.+?)(?=;|$)', line).group(1)
			#	#if not cds_id.startswith(mrna_id):
			#	#	print('GFF3 not sorted properly! This script expects a nested format with gene first and its subordinate features after', file=sys.stderr)
			#	start = int(re.search('\sCDS\s+(\d+)\s', line).group(1))
			#	end = int(re.search('\d+\s+(\d+)\s', line).group(1))
			#	length = end - start +1

# Sort exon lists
for mrna in mrnas:
	mrnas[mrna][1].sort(key=lambda x:x[1])

# Check if any genes begin with an intron THIS IS NOT NECESSARY - THE FIRST PART OF THE EXON MAY BE A UTR
#for gene in genes:
#	gene_start = genes[gene][0][0]
#	first_exon_start = genes[gene][1][0][0]
#	if not gene_start == first_exon_start:
#		print('First exon beyond gene start\t{0}'.format(gene), file=sys.stderr)
#		print(gene_start, first_exon_start, file=sys.stderr)
#		print(genes[gene], file=sys.stderr)

# Build intron stats dict
introns = {}
exons = {}
for mrna in mrnas:
	exons[mrna] = [ (e[1] - e[0]) +1 for e in mrnas[mrna][1] ]
	introns[mrna] = [ (mrnas[mrna][1][i][0] - mrnas[mrna][1][i-1][1]) -1 for i in range(1,len(mrnas[mrna][1])) ]

# Output gene stats
with open(out_prefix + '.exon_lengths', 'w') as exon_out_fl:
	for locus in exons:
		for exon in exons[locus]:
			exon_out_fl.write('{0}\t{1}\n'.format(locus, exon))
with open(out_prefix + '.locus_exon_counts', 'w') as exon_locus_counts_fl:
	for locus in exons:
		exon_locus_counts_fl.write('{0}\t{1}\n'.format(locus,len(exons[locus])))
with open(out_prefix + '.intron_lengths', 'w') as intron_out_fl:
	for locus in introns:
		for intron in introns[locus]:
			intron_out_fl.write('{0}\t{1}\n'.format(locus, intron))
with open(out_prefix + '.locus_intron_counts', 'w') as intron_locus_counts_fl:
	for locus in introns:
		intron_locus_counts_fl.write('{0}\t{1}\n'.format(locus, len(introns[locus])))
with open(out_prefix + '.gene_lengths', 'w') as gene_lengths_fl:
	for gene in genes:
		gene_lengths_fl.write('{0}\t{1}\n'.format(gene, genes[gene][1]))
#with open(out_prefix + '.various', 'w') as gene_summary_fl:
#	total_intron_length = 0.0
#	total_exon_length = 0.0
#	for locus in introns:
#		total_intron_length += sum(introns[locus])
#		total_exon_length += sum(exons[locus])
#	
#	total_genic_length = total_intron_length + total_exon_length
#	gene_summary_fl.write('genic\t{0}\t{1}\n'.format(total_genic_length, total_genic_length/total_genic_length))
#	gene_summary_fl.write('genic_intron\t{0}\t{1}\n'.format(total_intron_length, total_intron_length/total_genic_length))
#	gene_summary_fl.write('genic_exon\t{0}\t{1}\n'.format(total_exon_length, total_exon_length/total_genic_length))
