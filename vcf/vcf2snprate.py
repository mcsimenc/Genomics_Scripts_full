#!/usr/bin/env python3

import sys

def help():
	print('''
 usage:
 	vcf2track.py -vcf <file> [-ref <file> -binsize <int>]

 description:
	
	If -ref is not used, Prints a Circos line track of SNP rate
	Then scaffold lengths are obtained from the vcf and used to
	calculate SNP rate. e.g. if the VCF represents mapped
	genomic reads.

	If -ref is used, only the features specified in the -ref
	GFF3 file are used. e.g. if the VCF represents mapped
	transcript reads.

 options:
	-binsize <int>  If not using -ref, bin size. Default 1000 (1kb)
	-ref		GFF3 of features to calculate SNP rate
	-noindels	Don't count indels
	-nosnps		Don't count snps
''', file=sys.stderr)
	sys.exit()

class GFF3_line:
	'''
	Attributes:
			field0, ... , field8 - string
			attributes - dictionary

	Methods:    str()		prints gff line
		    refreshAttrStr()	updates gff line attributes (needed if changes to attributes were made)

	kwargs is a dictionary
	'''
	def __init__(self, line=None, **kwargs):

		if line == None:
			(self.seqid, self.source, self.type, self.start, self.end, self.score, self.strand, self.phase, self.attributes_str) = [None]*9
			self.attributes_order = []
			self.attributes = {}
		else:
			(self.seqid, self.source, self.type, self.start, self.end, self.score, self.strand, self.phase, self.attributes_str) = line.strip().split('\t')
			self.start = int(self.start)
			self.end = int(self.end)
			assert self.start <= self.end
			self.coords = (self.start, self.end)
			self.length = self.end - self.start + 1
			attributes_list = self.attributes_str.split(';')
			self.attributes_order = [ attr.split('=')[0] for attr in attributes_list ]
			self.attributes = { attr.split('=')[0]:attr.split('=')[1] for attr in attributes_list }

		self.line_number = None
		if 'line_number' in kwargs:	
			self.line_number = kwargs['line_number']
		# rename the name attribute so it conforms to GFF3 specifications, where Name is a reserved attribute key. The version of LTRDigest makes attribute key name
		if 'name' in self.attributes:
			self.attributes['Name'] = self.attributes.pop('name')
			self.attributes_order[self.attributes_order.index('name')] = 'Name'

	def __repr__(self):
		'''
		Defines str() and repr() behavior
		'''
		self.refreshAttrStr()
		return '\t'.join( [ str(self.seqid), str(self.source), str(self.type), str(self.start), str(self.end), str(self.score), str(self.strand), str(self.phase), str(self.attributes_str) ] )

	def refreshAttrStr(self, attrOrder=None):
		'''
		If the attributes have been changed this needs to be called
		before the changes are reflected on a str() call on this object.

		If an attribute has been added it should have also been added to self.attributes_order
		'''
		self.attributes_str = ';'.join([ '='.join([ attr, self.attributes[attr] ]) for attr in self.attributes_order ])


	def addAttr(self, attr_key, attr_val, replace=False, attr_pos=0):
		'''
		Adds attribute, default is at the start of the list.
		Default behavior is to add attr_val to a growing
		comma-sep list if attr_key exists. Set replace=True to
		replace existing attr_val.
		'''
		if attr_key in self.attributes:
			if replace:
				delAttr(attr_key)
				self.attributes[attr_key] = attr_val
				self.attributes_order.insert(attr_pos, attr_key)
				self.refreshAttrStr()
			else: # grow list
				self.attributes[attr_key] = '{0},{1}'.format(self.attributes[attr_key], attr_val)
				self.refreshAttrStr()
		else:
			self.attributes[attr_key] = attr_val
			self.attributes_order.insert(attr_pos, attr_key)
			self.refreshAttrStr()

	def delAttr(self, attr_key):
		'''
		Deletes attribute.
		'''
		del self.attributes[attr_key]
		self.attributes_order.pop(self.attributes_order.index(attr_key))
		self.refreshAttrStr()

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

def read_ref_coords(gff3):
	'''
	reads all features and returns a dict:
	{scaf:{(start,end):gene_name}}
	'''
	dct = {}
	by_name = {}
	with open(gff3, 'r') as inFl:
		for line in inFl:
			if line.startswith('#'):
				continue
			g = GFF3_line(line)
			if g.seqid in dct:
				dct[g.seqid][g.coords] = g.attributes['Name']
			else:
				dct[g.seqid] = {g.coords:g.attributes['Name']}
			by_name[g.attributes['Name']] = g
	return dct, by_name

def Overlaps(j, k):
	'''
	Inputs, j and k, are tuples/lists with a start and a end coordinate as in: (start, end)
	If they overlap True is returned, if they do not overlap, False is returned.
	'''
	j = sorted([int(i) for i in j])
	k = sorted([int(i) for i in k])
	jk = sorted([j,k], key=lambda x:x[0])
	if jk[0][1] >= jk[1][0]:
		return True
	else:
		return False

def vcfref2snprate(vcf, ref, transformation='length', SNPS=True, INDELS=False):
	'''
	'''
	Ref, gff3 = read_ref_coords(ref)
	snps = {}
	with open(vcf, 'r') as inFl:
		for line in inFl:
			# Read in contig lengths
			if line.startswith('#'):
				continue
			line = line.strip().split('\t')
			contig = line[0]
			pos = int(line[1])

			# Do not/count SNPs or indels
			if typ == 'INDEL':
				if not INDELS:
					continue
			else:
				if not SNPS:
					continue

			if contig not in Ref:
				continue
			for coord in Ref[contig]:
				if Overlaps(coord, (pos,pos)):
					gene_name = Ref[contig][coord]
					if gene_name in snps:
						snps[gene_name] += 1
					else:
						snps[gene_name] = 1
	print('gene\tgene_length\tSNPs\tSNPs/length')
	for gene_name in snps:
		length, SNPs, ratio = [gff3[gene_name].length, snps[gene_name], snps[gene_name]/gff3[gene_name].length]
		print('{0}\t{1}\t{2}\t{3:.5f}'.format(gene_name, length, SNPs, ratio))
			
def vcf2heatmap(vcf, binsize=1000, SNPS=True, INDELS=False):
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
			typ = line[7].split(';')[0]

			# Do not/count SNPs or indels
			if typ == 'INDEL':
				if not INDELS:
					continue
			else:
				if not SNPS:
					continue

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

	if '-noindels' in args:
		INDELS = False
	else:
		INDELS = True

	if '-nosnps' in args:
		SNPS = False
	else:
		SNPS = True

	if '-binsize' in args:
		binsize = int(args[args.index('-binsize')+1])
	else:
		binsize = 1000

	if '-ref' in args:
		refPth = args[args.index('-ref')+1]

	vcfPth = args[args.index('-vcf')+1]
	if '-ref' in args:
		vcfref2snprate(vcfPth, refPth, SNPS=SNPS, INDELS=INDELS)
	else:
		vcf2heatmap(vcfPth, binsize=binsize, SNPS=SNPS, INDELS=INDELS)
