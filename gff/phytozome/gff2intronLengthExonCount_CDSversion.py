#!/usr/bin/env python3

import sys

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
			self.attributes_order[self.attributes_order.index('name')] = 'Name'

	def __repr__(self): # for when str() or repr() are called

		return '\t'.join( [ str(self.seqid), str(self.source), str(self.type), str(self.start), str(self.end), str(self.score), str(self.strand), str(self.phase), str(self.attributes_str) ] )

	def refreshAttrStr(self, attrOrder=None):
		'''
		If the attributes have been changed this needs to be called
		before the changes are reflected on a str() call on this object.

		If an attribute has been added it should have also been added to self.attributes_order
		'''
		self.attributes_str = ';'.join([ '='.join([ attr, self.attributes[attr] ]) for attr in self.attributes_order ])


def help():
	print('''
		Usage:
		------------
		gffMakerGFF-intronLengths.py < input.gff > output.txt

		Description:
		------------
		Calculates all intron lengths. Outputs intron lengths to
		stdout and exon counts to stderr. -gff option outputs
		intron GFF to stdout.

		Options:
		------------

		''')
	sys.exit(0)


# Get parameters
args = sys.argv

# If asked for help or insufficient parameters
if "-help" in args or "-h" in args:
	help()


exon_count = None
last_exon_end = float('-inf')
gene = None
last_scaf = None


for line in sys.stdin:
	if not line.startswith('#'):
		contents = line.strip().split('\t')
		if contents[2] == 'gene':
			if not exon_count == None:
				print('{0}\t{1}'.format(gene, exon_count), file=sys.stderr)

			exon_count = 0
			last_exon_end = float('-inf')
			gene = contents[8].split(';')[0].split('=')[1]
			continue
		elif contents[2] == 'CDS':
			#if last_scaf == contents[0] and int(contents[3]) > last_exon_end and not last_exon_end == float('-inf'):
			#	continue
			if not last_exon_end == float('-inf'):
				intronStart = last_exon_end + 1
				intronEnd = int(contents[3]) - 1
				if not intronEnd > intronStart:
					continue
				intronLen = intronEnd - intronStart + 1
				print('{0}\t{1}'.format(gene, intronLen))
				last_exon_end = int(contents[4])
				last_scaf = contents[0]
			
			else:
				last_exon_end = int(contents[4])
				last_scaf = contents[0]
			exon_count += 1

print('{0}\t{1}'.format(gene, exon_count), file=sys.stderr)
		



#Azfi_s4729	maker	gene	5003	7129	.	-	.	ID=Azfi_s4729.g121372;Name=Azfi_s4729.g121372
#Azfi_s4729	maker	exon	5003	5016	.	-	.	ID=Azfi_s4729.g121372-mRNA-1:exon:9237;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	CDS	5003	5016	.	-	2	ID=Azfi_s4729.g121372-mRNA-1:cds;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	mRNA	5003	7129	.	-	.	ID=Azfi_s4729.g121372-mRNA-1;Parent=Azfi_s4729.g121372;Name=Azfi_s4729.g121372-mRNA-1;_AED=0.85;_eAED=0.85;_QI=0|0|0|0.16|1|1|6|0|234
#Azfi_s4729	maker	exon	5089	5240	.	-	.	ID=Azfi_s4729.g121372-mRNA-1:exon:9238;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	CDS	5089	5240	.	-	1	ID=Azfi_s4729.g121372-mRNA-1:cds;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	exon	5466	5612	.	-	.	ID=Azfi_s4729.g121372-mRNA-1:exon:9239;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	CDS	5466	5612	.	-	1	ID=Azfi_s4729.g121372-mRNA-1:cds;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	exon	5796	5842	.	-	.	ID=Azfi_s4729.g121372-mRNA-1:exon:9240;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	CDS	5796	5842	.	-	0	ID=Azfi_s4729.g121372-mRNA-1:cds;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	exon	6200	6480	.	-	.	ID=Azfi_s4729.g121372-mRNA-1:exon:9241;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	CDS	6200	6480	.	-	2	ID=Azfi_s4729.g121372-mRNA-1:cds;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	exon	7066	7129	.	-	.	ID=Azfi_s4729.g121372-mRNA-1:exon:9242;Parent=Azfi_s4729.g121372
#Azfi_s4729	maker	CDS	7066	7129	.	-	0	ID=Azfi_s4729.g121372-mRNA-1:cds;Parent=Azfi_s4729.g121372
