#!/usr/bin/env python3

# usage:
#	script Ps STs ST2Pmap Ts T2Pmap Psnp
#
#	s1-3	directories with salmon quant files for same libraries
#	snp	snps from phyozome12 annot bcftools

import sys
import os

def add_salmon_runs(dct, quant_dir, label, Map=None, col='counts', ADD=True, revmap=False):
	'''
	Default format for map input is PhytozomeGene\tOtherGene\n
	revap=True will flip the order, so the
	Phytozome gene is in the second column. We did this for Trinity map

	quant_dir should be have files named
	like library1.fq.quant which are the
	quant.sf output by salmon.

	col can be counts or TPM.

	ADD=False means new names will not be added
	 we run this with ADD=True for the Phytozome quantitations
	 then ADD=False for the StringTie and Trinity quantitations
	'''
	if Map:
		M = {} # TranscriptName:PhytozomeName
		with open(Map) as inFl:
			for line in inFl:
				line = line.strip().split()
				#print('{0}\t{1}'.format(line[0],line[1]))
				if revmap:
					M[line[0]] = line[1]
				else:
					M[line[1]] = line[0]
			#Map = {l.split('\t')[0]:l.split('\t')[1] for l in open(Map).read().split('\n')}
		#for k in M:
		#	print(k)
	#print(list(dct.keys()))
	for run in [f for f in os.listdir(quant_dir) if f.endswith('quant')]:
		lib = run.rstrip('.quant')
		with open(quant_dir+'/'+run) as inFl:
			for line in inFl:
				if line.startswith('Name\t'):
					continue
				name, length, effectivelength, tpm, numreads = line.strip().split()
				numreads = float(numreads)
				if Map:
					if label == 'stringtie':
						name = '.'.join(name.split('.')[:-1])
					if name in M:
						name = M[name]
					else:
						# These StringTie genes have no Phytozome counterpart
						continue
				if not ADD:
					if name not in dct:
						continue
				if col == 'counts':
					if name not in dct:
						dct[name] = {label:{lib:numreads}}
					else:
						if label not in dct[name]:
							dct[name][label] = {lib:numreads}
						else:
							if lib in dct[name][label]:
								# multiple Trinity transcripts may map to a single Phytozome gene,
								dct[name][label][lib] += numreads
							else:
								dct[name][label][lib] = numreads
				# Not good for Trinity b/c no implementation for combining multiple TPMs (for Trinity transcripts)
				elif col == 'TPM':
					if name not in dct:
						dct[name] = {label:{lib:tpm}}
					else:
						if label not in dct[name]:
							dct[name][label] = {lib:tpm}
						else:
							dct[name][label][lib] = tpm
	return dct

def add_snps(dct, snps):
	'''
	Adds Variant Calling data from script 
	'''
	with open(snps) as inFl:
		label = 'VariantCalling'
		for line in inFl:
			if line.startswith('gene\t'): # header
				continue

			name, length, polymorphisms, ratio_p, snps, ratio_s = line.strip().split('\t')
			#gene	gene_length	SNPs	SNPs/length
			#MDP0000145017	1975	2	0.00101
			#MDP0000322439	15359	33	0.00215
			if name not in dct:
				dct[name] = {label:{'gene_length':length, 'polymorphisms':polymorphisms, 'polymorphisms/gene_length':ratio_p, 'snps_count':snps, 'snps/gene_length':ratio_s}}
			else:
				if label not in dct[name]:
					dct[name][label] = {'gene_length':length, 'polymorphisms':polymorphisms, 'polymorphisms/gene_length':ratio_p, 'snps_count':snps, 'snps/gene_length':ratio_s}
				else:
					sys.exit('should not have multiple SNP field sets')
	return dct
		
		
def print_salmon_runs(data):
	'''
	Prints libraries in sorted order to make sure rows line up
	data needs to be of the form:
	{ gene_name: {phytozome: {Sample_11}:102}}
	'''
	# print header
	header = 'gene_name'
	Names = sorted(list(data.keys())) # row name
	Labels = set()
	for name in Names:
		for n in data[name].keys(): # Trinity, StringTie, etc. 
			Labels.add(n)
	Labels = sorted(list(Labels))
	for name in Names: # Make sure current 'name' has all 4 labels for printing header
		if len(data[name]) == len(set(Labels)):
			break
	for label in Labels:
		Libraries = sorted(list(data[name][label]))
		for lib in Libraries:
			header = header + '\t{0}_{1}'.format(label,lib)
	print(Labels, file=sys.stderr)
	print(header, end='')

	# print data
	for name in Names:
		# Skip rows lacking all 4 labels
		if len(data[name]) != len(set(Labels)):
			continue
		line = ''
		line += '\n' + name
		SKIP = False
		for label in Labels:
			if label not in data[name]:
				SKIP = True
		if SKIP:
			continue

		for label in Labels:
			Libraries = sorted(list(data[name][label]))
			for lib in Libraries:
				line = line+'\t'+str(data[name][label][lib])
			#if label == 'VariantCalling':
			#	for field in data[name][label]:
			#		line = line+'\t'+data[name][label][field]
			#else:
			#	for lib in Libraries:
			#		line = line+'\t'+data[name][label][lib]
		print(line, end='')

#Name	Length	EffectiveLength	TPM	NumReads
#MDP0000133028	1344	1824.783	0.196967	4.449
#MDP0000360951	438	284.025	0.000000	0.000
#MDP0000466557	1551	1450.523	0.556740	9.997
#MDP0000184486	504	250.000	0.987182	3.055
#MDP0000184487	1902	2838.019	0.654671	23.000
#MDP0000147446	429	180.000	0.000000	0.000
#MDP0000292452	612	365.020	31.919757	144.233
#MDP0000140112	1515	250.000	0.000000	0.000
#MDP0000897960	300	52.000	0.000000	0.000

if __name__ == '__main__':
	args = sys.argv
	if len(args) < 2 or '-h' in args:
		print('''
 usage:
	quant-snp-matrix.py <SNPs> <Psalmon> <STsalmon> <STmap> <Tsalmon> <Tmap> [Options]

 description:
 	Takes in directories contining salmon quant.sf files renamed like: <library_name>.quant
	Psalmon - Phytozome salmon
	STsalmon - StringTie salmon
	Tsalmon - Trinity salmon
	Tmap, STmap - mappings of Phytozome gene names to StringTie and Trinity transcript names
	SNPs - a file output by vcf2snprate.py used with -ref
''', file=sys.stderr)
		sys.exit()

	phytozome_snps = args[1]
	phytozome_quant_dir = args[2]
	stringtie_quant_dir = args[3]
	stringtie_phytozome_map = args[4]
	trinity_quant_dir = args[5]
	trinity_phytozome_map = args[6]

	print('#1 Adding Phytozome data ...', file=sys.stderr)
	data = add_salmon_runs({}, phytozome_quant_dir, Map=None, label='phytozome')
	print('#2 Adding StringTie data ...', file=sys.stderr)
	data = add_salmon_runs(data, stringtie_quant_dir, Map=stringtie_phytozome_map, label='stringtie', ADD=False)
	print('#3 Adding Trinity data ...', file=sys.stderr)
	data = add_salmon_runs(data, trinity_quant_dir, Map=trinity_phytozome_map, label='trinity', ADD=False, revmap=True)
	print('#4 Adding BCFtools data ...', file=sys.stderr)
	data = add_snps(data, phytozome_snps)

	print_salmon_runs(data)
