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



last_gffLine = None
gffLine = None

for line in sys.stdin:
	if line.startswith('#'):
		print(line, end='')
	else:
		gffLine = GFF3_line(line)
		if last_gffLine != None:
			if 'Name' in gffLine.attributes and 'Name' in last_gffLine.attributes:
				lastName = last_gffLine.attributes['Name']
				thisName = gffLine.attributes['Name']
				lastScaf = last_gffLine.seqid
				thisScaf = gffLine.seqid
				if lastName == thisName and thisName == 'Satellite_centromeric_repeat' and lastScaf == thisScaf:
					if int(last_gffLine.end) >= int(gffLine.start)-1:
						last_gffLine.end = gffLine.end
					else:
						print(str(last_gffLine))
						last_gffLine = gffLine
				else:
					print(str(last_gffLine))
					last_gffLine = gffLine
			else:
				print(str(last_gffLine))
				last_gffLine = gffLine
		else:
			last_gffLine = gffLine

print(str(last_gffLine))

