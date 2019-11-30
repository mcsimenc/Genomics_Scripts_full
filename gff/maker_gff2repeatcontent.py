#!/usr/bin/env python3

import os
import sys
import subprocess
import re

#qsub_stdout = subprocess.check_output('qsub {0}{1}.qsub'.format(self.output_dir, self.opt_dct['name']), shell=True)

#subprocess.call('maker2zff -n {0}*all.gff'.format(self.output_dir), cwd=self.output_dir, shell=True)

def help():
	print('''
		Usage:
		------------
		python3 maker_gff2genomeContent.py -f <gff> [options]

		Description:
		------------
		Outputs repeat stats or gene, exon, and intron stats from an input GFF3

		Output:
		------------
		-r	col 1	genus
			col 2	num occurrences
			col 3	total length
			col 4	proportion of genome that is this genus

		-g	1. gene name + intron length
			2. gene name + exon length
			2. gene name + exon number
			2. gene name + intron number


		Options:
		------------
		-f	Path to input maker gff3 file (mandatory).

		-g	Output gene stats. 2 files name prefixed by name given by -o opt.
			[prefix].exon_lengths and [prefix].intron_lengths

		-p	Output files prefix.

		-r	Output repeat stats.

		-s	Assembly size in bases.
			Salvinia cucullata first assembly: 222099292
			Salvinia cucullata v1: 225872744
			Salvinia cucullata v1.1: 232832424
			Azolla filiculoides (celera asm, quivered): 692828876
		''')

args = sys.argv

if '-h' in args:
	help()
	sys.exit()

try:
	gff = args[args.index('-f') + 1]
	out_prefix = args[args.index('-p') + 1]
	genome_size = int(args[args.index('-s') +1])
except:
	help()
	sys.exit()


wd = os.getcwd()

# extract features of interest from gff and put in another file
grep_features_call = "grep -E '(repeatmasker\smatch\s)|(maker\sgene\s)|(maker\sexon\s)|(maker\sCDS\s)' < {0} | awk '{{print $3 \"\t\" $4 \"\t\" $5 \"\t\" $9}}' > features_subgff.tmp".format(gff)
subprocess.call(grep_features_call, cwd=wd, shell=True)



# repeat info, all types of repeats kept separate
repeats = {}
# repeat info for short output (lumps repeat types, e.g. LTR)
shrt_repeats = {}
genes = {}
genes_cds = {}
total_genic_length = 0
with open('features_subgff.tmp','r') as feature_fl:

	for line in feature_fl:

		# Get repeat lengths and types
		if '-r' in args:
			if line.startswith('match'):

				start = int(re.search('^match\s(\d+?)\s', line).group(1))
				end = int(re.search('\d+\s(\d+?)\s', line).group(1))
				length = end - start +1

				id = re.search('Name=species:(.+);', line).group(1)
				genus = re.search('genus:(.+)', id).group(1)
				species = re.search('(^.+)\|', id).group(1)

				try:
					repeats[genus][0].append(species)
					repeats[genus][1].append(length)
				except KeyError:
					repeats[genus] = [ [species], [length] ]

		# Get gene lengths
		if '-g' in args:
			if line.startswith('gene'):

				id = re.search('ID=(.+?)(?=;|$)', line).group(1)
				#print('gene\t{0}'.format(id))
				start = int(re.search('^gene\s(\d+)\s', line).group(1))
				end = int(re.search('\d+\s(\d+)\s', line).group(1))
				length = end - start +1
				total_genic_length += length

				if not id in genes:
					genes[id] = [(start,end),[]]
					genes_cds[id] = [(start,end),[]]
				else:
					print('Duplicate Gene?\t{0}'.format(id), file=sys.stderr)

			elif line.startswith('exon'):

				id = re.search('Parent=(.+?)(?=-mRNA)', line).group(1)
				#print('exon\t{0}'.format(id))
				start = int(re.search('^exon\s(\d+)\s', line).group(1))
				end = int(re.search('\d+\s(\d+)\s', line).group(1))
				length = end - start +1

				if not id in genes:
					print('Genes and exons out of order?\t{0}'.format(id), file=sys.stderr)
				else:
					genes[id][1].append((start,end))

			elif line.startswith('CDS'):

				id = re.search('Parent=(.+?)(?=-mRNA)', line).group(1)
				#print('CDS\t{0}'.format(id))
				start = int(re.search('^CDS\s+(\d+)\s', line).group(1))
				end = int(re.search('\d+\s+(\d+)\s', line).group(1))
				length = end - start +1

				if not id in genes_cds:
					print('Genes and CDS out of order?\t{0}'.format(id), file=sys.stderr)
				else:
					#genes_cds[id][1].append((start,end))
					genes_cds[id][1].append(length)

if '-g' in args:
	# Sort exon lists
	for gene in genes:
		genes[gene][1].sort(key=lambda x:x[1])

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
	for gene in genes:
		exons[gene] = [ (e[1] - e[0]) +1 for e in genes[gene][1] ]
		introns[gene] = [ (genes[gene][1][i][0] - genes[gene][1][i-1][1]) -1 for i in range(1,len(genes[gene][1])) ]

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
	with open(out_prefix + '.various', 'w') as gene_summary_fl:
		total_intron_length = 0.0
		total_exon_length = 0.0
		total_cds_length = 0.0
		for locus in introns:
			total_intron_length += sum(introns[locus])
			total_exon_length += sum(exons[locus])
			total_cds_length += sum(genes_cds[locus][1])
		
		total_genic_length = total_intron_length + total_exon_length
		gene_summary_fl.write('genic\t{0}\t{1}\n'.format(total_genic_length, total_genic_length/total_genic_length))
		gene_summary_fl.write('genic_intron\t{0}\t{1}\n'.format(total_intron_length, total_intron_length/total_genic_length))
		gene_summary_fl.write('genic_exon\t{0}\t{1}\n'.format(total_exon_length, total_exon_length/total_genic_length))
		gene_summary_fl.write('genic_CDS\t{0}\t{1}\n'.format(total_cds_length, total_cds_length/total_genic_length))


if '-r' in args:

	kinds = ['Retrotransposon', 'DNA', 'LINE', 'SINE', 'Other', 'LTR', 'Satellite', 'Low_complexity', 'ARTEFACT', 'Unspecified', 'tRNA', 'rRNA', 'Simple_repeat', 'RC', 'snRNA']

	for genus in repeats:

		data_added = False

		for group in kinds:

			if genus.startswith(group):

				try:
					shrt_repeats[group][0] = shrt_repeats[group][0] + repeats[genus][0]
					shrt_repeats[group][1] = shrt_repeats[group][1] + repeats[genus][1]
				except KeyError:
					shrt_repeats[group] = [ repeats[genus][0], repeats[genus][1] ]

				data_added = True

				break

		if data_added == False:

			try:
				shrt_repeats[genus][0] = shrt_repeats[genus][0] + repeats[genus][0]
				shrt_repeats[genus][1] = shrt_repeats[genus][1] + repeats[genus][1]
			except KeyError:
				shrt_repeats[genus] = [ repeats[genus][0], repeats[genus][1] ]

	shrt_repeats_types = sorted(list(shrt_repeats.keys()))
	full_repeats_types = sorted(list(repeats.keys()))


	# write long repeat output
	with open('{0}_repeat_summary_full'.format(out_prefix), 'w') as out_fl:

		total_length = sum([i for genus in repeats for i in repeats[genus][1] ]) + total_genic_length

		for kind in full_repeats_types:
			out_fl.write('{0}\t'.format(kind))
			out_fl.write('{0}\t'.format(str(len(repeats[kind][0]))))
			out_fl.write('{0}\t'.format(str(sum(repeats[kind][1]))))
			out_fl.write('{0}\n'.format(str(round(sum(repeats[kind][1])/float(genome_size), 10))))

		out_fl.write('{0}\t'.format('Genic'))
		out_fl.write('{0}\t'.format('1'))
		out_fl.write('{0}\t'.format(str(total_genic_length)))
		out_fl.write('{0}\n'.format(str(round((total_genic_length)/float(genome_size), 10))))

		out_fl.write('{0}\t'.format('Rest_of_genome'))
		out_fl.write('{0}\t'.format('1'))
		out_fl.write('{0}\t'.format(str(genome_size - total_length)))
		out_fl.write('{0}\n'.format(str(round((genome_size - total_length)/float(genome_size), 10))))
		

	# write short repeat output
	with open('{0}_repeat_summary_short'.format(out_prefix), 'w') as out_fl:

		total_length = sum([i for genus in shrt_repeats for i in shrt_repeats[genus][1] ]) + total_genic_length

		for kind in shrt_repeats_types:
			out_fl.write('{0}\t'.format(kind))
			out_fl.write('{0}\t'.format(str(len(shrt_repeats[kind][0]))))
			out_fl.write('{0}\t'.format(str(sum(shrt_repeats[kind][1]))))
			out_fl.write('{0}\n'.format(str(round(sum(shrt_repeats[kind][1])/float(genome_size), 10))))

		out_fl.write('{0}\t'.format('Genic'))
		out_fl.write('{0}\t'.format('1'))
		out_fl.write('{0}\t'.format(str(total_genic_length)))
		out_fl.write('{0}\n'.format(str(round((total_genic_length)/float(genome_size), 10))))

		out_fl.write('{0}\t'.format('Rest_of_genome'))
		out_fl.write('{0}\t'.format('1'))
		out_fl.write('{0}\t'.format(str(genome_size - total_length)))
		out_fl.write('{0}\n'.format(str(round((genome_size - total_length)/float(genome_size), 10))))
