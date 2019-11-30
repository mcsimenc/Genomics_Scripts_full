#!/usr/bin/env python3

import sys
import re


if '-h' in sys.argv:
	print('''
			usage:
				geneName -map <file> < <file.gff> > output.gff


			description: removes score and attributes from GFF3 input
				     and combines any overlapping features. Strand
				     is ignored. Genes found to not have anotations
				     are reported to stderr unless -stderr is used

				     -map	a two column mapping of gene names to
				     		annotations with which to modify gene
						names.

				     -nostderr  suppress stderr output

		''')
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
	def __init__(self, line, **kwargs):

		(self.seqid, self.source, self.type, self.start, self.end, self.score, self.strand, self.phase, self.attributes_str) = line.strip().split('\t')
		self.line_number = None

		if 'line_number' in kwargs:	
			self.line_number = kwargs['line_number']

		attributes_list = self.attributes_str.split(';')
		self.attributes_order = [ attr.split('=')[0] for attr in attributes_list ]
		self.attributes = { attr.split('=')[0]:attr.split('=')[1] for attr in attributes_list }

		# rename the name attribute so it conforms to GFF3 specifications, where Name is a reserved attribute key. The version of LTRDigest makes attribute key name
		if 'name' in self.attributes:
			self.attributes['Name'] = self.attributes.pop('name')

	def __repr__(self): # for when str() or repr() are called

		return '\t'.join( [ str(self.seqid), str(self.source), str(self.type), str(self.start), str(self.end), str(self.score), str(self.strand), str(self.phase), str(self.attributes_str) ] )

	def refreshAttrStr(self, attrOrder=None):
		'''
		If the attributes have been changed this needs to be called
		before the changes are reflected on a str() call on this object.
		'''
		self.attributes_str = ';'.join([ '='.join([ attr, self.attributes[attr] ]) for attr in self.attributes_order ])



annotMap = {}
with open(sys.argv[sys.argv.index('-map') + 1]) as mapFl:
	for line in mapFl:
		gene, annot = line.strip().split('\t')
		annotMap[gene] = annot


for line in sys.stdin:
	if not line.startswith('#'):
		
		gffLine = GFF3_line(line)

		if 'trnascan' not in gffLine.attributes_str:

			for attr in ['ID', 'Name', 'Parent']:

				if attr in gffLine.attributes:
					geneNameMatch = re.search('(.+?exonerate_protein2genome-gene-[\d]\.[\d]+)', gffLine.attributes[attr])
					geneName = geneNameMatch.group(1)
					splitGeneName = gffLine.attributes[attr].split('exonerate_protein2genome-gene')
					if geneName in annotMap:
						splitGeneName.insert(1,annotMap[geneName])
						newGeneName = ''.join(splitGeneName)
						gffLine.attributes[attr] = newGeneName
					else:
						if '-nostderr' not in sys.argv:
							print('No_annotation_for:\t{0}'.format(geneName), file=sys.stderr)
						splitGeneName[0] = splitGeneName[0].strip('-')
						newGeneName=''.join(splitGeneName)
						gffLine.attributes[attr] = newGeneName

			gffLine.refreshAttrStr()
		print(str(gffLine))
	else:
		print(line, end='')


		



#Acas.4051_0001	maker	gene	12849	16043	.	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12;Name=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12
#Acas.4051_0001	maker	mRNA	12849	16043	3195	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12-mRNA-1;Parent=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12;Name=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12-mRNA-1;_AED=0.35;_eAED=0.35;_QI=0|-1|0|1|-1|0|1|0|1064
#Acas.4051_0001	maker	exon	12849	16043	.	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12-mRNA-1:exon:0;Parent=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12-mRNA-1
#Acas.4051_0001	maker	CDS	12849	16043	.	+	0	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12-mRNA-1:cds;Parent=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.12-mRNA-1
#Acas.4051_0001	maker	gene	20802	23126	.	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8;Name=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8
#Acas.4051_0001	maker	mRNA	20802	23126	2325	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8-mRNA-1;Parent=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8;Name=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8-mRNA-1;_AED=0.39;_eAED=0.40;_QI=0|-1|0|1|-1|0|1|0|774
#Acas.4051_0001	maker	exon	20802	23126	.	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8-mRNA-1:exon:1;Parent=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8-mRNA-1
#Acas.4051_0001	maker	CDS	20802	23126	.	+	0	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8-mRNA-1:cds;Parent=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.8-mRNA-1
#Acas.4051_0001	maker	gene	16070	18857	.	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.6;Name=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.6
#Acas.4051_0001	maker	mRNA	16070	18857	2040	+	.	ID=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.6-mRNA-1;Parent=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.6;Name=maker-Acas.4051_0001-exonerate_protein2genome-gene-0.6-mRNA-1;_AED=0.41;_eAED=0.41;_QI=0|0|0|1|0|0|2|0|679
