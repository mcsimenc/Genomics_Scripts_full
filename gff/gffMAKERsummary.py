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

print('gene\tAED\teAED\tfracExonsWithOnlyTranscriptSupport\tfracExonsWithOnlyProteinSupport\tfracExonsWithTranscriptAndProteinSupport\tfracExonsWithSNAPsupport')

for line in sys.stdin:
	if not line.startswith('#'):

		gffLine = GFF3_line(line)

		if gffLine.type == 'mRNA':
			name = gffLine.attributes['Parent']
			AED = float(gffLine.attributes['_AED'])
			eAED = float(gffLine.attributes['_eAED'])
			QI = gffLine.attributes['_QI'].split('|')
			T = float(QI[2]) # frac exons with transcript support
			ToP = float(QI[3]) # frac exons with transcript or protein support
			Po = ToP - T # frac exons with only protein support
			To = T - ToP # frac exons with only transcript support
			TaP = ToP - (To + Po) # frac exons with transcript support and protein support
			S = QI[5] # frac exons with SNAP support
			
			if AED < 0:
				print(line)
				sys.exit()
			#if eAED < 0:
			#	print(line)
			#	sys.exit()

			print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(name, AED, eAED, To, Po, TaP, S))



#Azfi_s0001	maker	mRNA	46283	58101	.	+	.	ID=Azfi_s0001.g000001-mRNA-1;Parent=Azfi_s0001.g000001;Name=Azfi_s0001.g000001-mRNA-1;_AED=0.21;_eAED=0.21;_QI=0|0.69|0.57|1|0.61|0.71|14|0|935
