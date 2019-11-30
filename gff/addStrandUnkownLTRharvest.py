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
	def __init__(self, line=None, **kwargs):

		if line == None:
			(self.seqid, self.source, self.type, self.start, self.end, self.score, self.strand, self.phase, self.attributes_str) = [None]*9
			self.attributes_order = []
			self.attributes = {}
			
		else:
			(self.seqid, self.source, self.type, self.start, self.end, self.score, self.strand, self.phase, self.attributes_str) = line.strip().split('\t')
			self.start = int(self.start)
			self.end = int(self.end)
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

	def __repr__(self): # for when str() or repr() are called

		return '\t'.join( [ str(self.seqid), str(self.source), str(self.type), str(self.start), str(self.end), str(self.score), str(self.strand), str(self.phase), str(self.attributes_str) ] )

	def refreshAttrStr(self, attrOrder=None):
		'''
		If the attributes have been changed this needs to be called
		before the changes are reflected on a str() call on this object.

		If an attribute has been added it should have also been added to self.attributes_order
		'''
		self.attributes_str = ';'.join([ '='.join([ attr, self.attributes[attr] ]) for attr in self.attributes_order ])

strands = {}
with open(sys.argv[1]) as strandFl:
	for line in strandFl:
		contents = line.strip().split()
		strands[contents[0]] = contents[2]

for line in sys.stdin:
	if not line.startswith('#'):
		gffLine = GFF3_line(line)
		if gffLine.strand == '?':
			if 'ID' in gffLine.attributes:
				num = gffLine.attributes['ID'].split('on')[-1]
			else:
				num = gffLine.attributes['Parent'].split('on')[-1]
			el = 'LTR_retrotransposon{0}'.format(num)
			if el in strands:
				strand = strands[el]
				gffLine.strand = strand
				print(str(gffLine))
			else:
				if 'LTRharvest' in line or 'LTRdigest' in line:
					gffLine.strand = '+'
					print(str(gffLine))
				else:
					print(line, end='')
		else:
			print(line, end='')
	else:
		print(line, end='')

			
#Azfi_s0001	LTRharvest	repeat_region	159726	166522	.	?	.	ID=repeat_region6
#Azfi_s0001	LTRharvest	target_site_duplication	159726	159729	.	?	.	Parent=repeat_region6
#Azfi_s0001	LTRharvest	LTR_retrotransposon	159730	166518	.	?	.	ID=LTR_retrotransposon6;Parent=repeat_region6;ltr_similarity=89.57;seq_number=0;dfam_2.0_annotation=None;repbase_22.04_annotation=Gypsy-4_PPa-I_Gypsy_Physcomitrella_patens
#Azfi_s0001	LTRharvest	long_terminal_repeat	159730	160007	.	?	.	Parent=LTR_retrotransposon6
#Azfi_s0001	LTRharvest	long_terminal_repeat	166247	166518	.	?	.	Parent=LTR_retrotransposon6
#Azfi_s0001	LTRharvest	target_site_duplication	166519	166522	.	?	.	Parent=repeat_region6
#Azfi_s0001	LTRharvest	repeat_region	248433	251697	.	?	.	ID=repeat_region12
#Azfi_s0001	LTRharvest	target_site_duplication	248433	248436	.	?	.	Parent=repeat_region12
#Azfi_s0001	LTRharvest	LTR_retrotransposon	248437	251693	.	?	.	ID=LTR_retrotransposon12;Parent=repeat_region12;ltr_similarity=97.27;seq_number=0;dfam_2.0_annotation=None;repbase_22.04_annotation=Gypsy-9_PPa-I_Gypsy_Physcomitrella_patens
#Azfi_s0001	LTRharvest	long_terminal_repeat	248437	248764	.	?	.	Parent=LTR_retrotransposon12
