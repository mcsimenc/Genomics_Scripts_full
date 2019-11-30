#!/usr/bin/env python3

import sys

def help():
	print('''
 usage:
 	vcf2track.py -vcf <file> [-binsize <int>]

 description:
	Prints a Circos line track of SNP rate

 options:
	-binsize default is 1000 (1kb)
''', file=sys.stderr)
	sys.exit()

def genbincoords(n, binsize):
	'''
	Returns the coordinates for the nth bins of size binsize
	'''
	return (n*binsize, (n+1)*binsize-1)

def getbins(length, binsize):
	'''
	Returns all the bins (including last small bin)
	'''
	if length//binsize == length/binsize:
		return tuple([ genbincoords(i, binsize) for i in range(length//binsize) ])
	else:
		return tuple([ genbincoords(i, binsize) for i in range(length//binsize) ] + [(genbincoords(length//binsize, binsize)[0],length)])

def vcf2heatmap(vcf, binsize=1000):
	'''
	Reads VCF file and outputs rate of SNPs per <binsize> to stdout
	'''
	contig_lengths = {}
	snps = {}
	with open(vcf, 'r') as inFl:
		last_contig = None
		for line in inFl:
			# Read in contig lengths
			if line.startswith('#'):
				if line.startswith('##contig='):
					##contig=<ID=MDC000001.73,length=2214>
					info = line.strip().split('contig=<')[1].rstrip('>').split(',')
					contig = info[0].split('=')[-1]
					length = int(info[1].split('=')[-1])
					contig_lengths[contig] = length
					continue
				else:
					continue

			# Count SNPs per bin
			#MDC044233.5	22580	.	AGG	AGGG	29.4193	.	INDEL;IDV=3;IMF=1;DP=3;VDB=0.764235;SGB=-0.511536;MQ0F=0.333333;AC=2;AN=2;DP4=0,0,0,3;MQ=22	GT:PL	1/1:59,9,0
			line = line.strip().split('\t')
			contig = line[0]
			pos = int(line[1])
			bin_no = pos//binsize
			if contig in snps:
				if bin_no in snps[contig]:
					snps[contig][bin_no] += 1
				else:
					snps[contig][bin_no] = 1
			else:
				snps[contig] = {bin_no:1}

	for contig in snps:
		for i, coords in enumerate(getbins(contig_lengths[contig], binsize)):
			try:
				snp_rate = snps[contig][i]/(coords[1]-coords[0]+1)
			except KeyError:
				snp_rate = 0
			print('{0}\t{1}\t{2}\t{3}'.format(contig, coords[0], coords[1], snp_rate))
			
if __name__ == '__main__':
	args = sys.argv

	if '-vcf' not in args or len(args) < 3:
		help()

	if '-binsize' in args:
		binsize = int(args[args.index('-binsize')+1])
	else:
		binsize = 1000

	vcfPth = args[args.index('-vcf')+1]
	vcf2heatmap(vcfPth, binsize=binsize)
