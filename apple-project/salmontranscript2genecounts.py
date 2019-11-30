#!/usr/bin/env python3

import sys
import os

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

if __name__ == '__main__':
	args = sys.argv
	if len(args) < 4 or '-h' in args:
		print('''
 usage:
	salmontranscript2genecounts.py <MakerFullGFF3> <SalmonQuantDir> <outputdir>

 description:
	For Trinity + MAKER models
	Populates outputdir with *quant files corresponding to the gene-level versions of the
	transcript-level files. This new dir is then to be used with quant-snp-matrix.py.
	
''', file=sys.stderr)
		sys.exit()

	_script, gff, tsalmon, out = sys.argv
	
	with open(gff, 'r') as inFl:
		for line in inFl:
			
	
	overlaps = {}
	M = {}
	for line in sys.stdin:
		if line.startswith('Gene ID'):
			continue
		
		gene_id, gene_name, scaf, strand, start, end, coverage, fpkm, tpm = line.strip().split()
		if gene_name != '-':
			if scaf in  overlaps:
				assert gene_name not in overlaps[scaf]
				overlaps[scaf][gene_name] = {strand:(start,end)}
			else:
				overlaps[scaf] = {gene_name:{strand:(start,end)}}
		else:
			if scaf not in overlaps:
				continue
			for g in overlaps[scaf]:
				if strand in overlaps[scaf][g]:
					if Overlaps(overlaps[scaf][g][strand], (start,end)):
						M[gene_id] = g
						print('{0}\t{1}'.format(M[gene_id],gene_id))

