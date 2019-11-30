#!/usr/bin/env python3

import sys

# This script takes two files as command-line arguments and outputs a list of genes from the second with AED < 1


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


args = sys.argv

hasSupport = []
with open(args[1]) as AEDfl:
	for line in AEDfl:
		contents = line.strip().split()
		if float(contents[4]) < 1:
			hasSupport.append('\tmaker\tmRNA\t{0}\t{1}\t'.format(contents[2], contents[3]))
			
#Azfi_s1615	mRNA	9106	11933	1.00
#Azfi_s1615	mRNA	6160	7091	1.00



with open(args[2]) as gffFl:
	for line in gffFl:
		if not line.startswith('#'):
			gffLine = GFF3_line(line)
			if gffLine.type == 'mRNA':
				for match in hasSupport:
					if match in line:
						print(gffLine.attributes['Parent'])
						break
