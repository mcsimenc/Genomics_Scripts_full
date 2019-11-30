#!/usr/bin/env python3

import sys

class GFF3_line:
	'''
	Attributes:
			field0, ... , field8 - string
			attributes - dictionary

	Methods:    str()		
				prints gff line
		    refreshAttrStr()
				updates gff line attributes
		    addAttr(key, val, replace=False, attr_pos=0)
				adds attr
		    delAttr(key)
				removes attr
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
	if len(args) < 3 or '-h' in args:
		print('''
 usage:
	script.py <makergff> <phytozomegff> <map>
 description:
	produces a map of trin transcripts to phytozome gene names
 options:
	-transcript	use feature type transcript instead of gene for <phytozomegff>
			this is to accommodate the use of stringtie gff
''', file=sys.stderr)
		sys.exit()


args = sys.argv

if '-transcript' in args:
	feat = 'transcript'
	attr = 'ID'
else:
	feat = 'gene'
	attr = 'Name'

# Map
Map = {}
gene, scaf, coords = [None]*3
# MAKER
with open(args[1]) as inFl:
	for line in inFl:
		if line.startswith('#'):
			continue
		if line.startswith('>'):
			break
		gff3Line = GFF3_line(line)
		if gff3Line.source == 'maker':
			if gff3Line.type == 'gene':
				gene = gff3Line.attributes['ID']
				scaf = gff3Line.seqid
				coords = (gff3Line.start, gff3Line.end)
				Map[gene] = set()
		elif gff3Line.source == 'est2genome':
			if gff3Line.type == 'expressed_sequence_match':
				if gene == None:
					continue
				if gff3Line.seqid == scaf:
					c2 = (gff3Line.start, gff3Line.end)
					if Overlaps(c2, coords):
						expr = gff3Line.attributes['Name']
						Map[gene].add(expr)
	#for g in Map:
	#	for e in Map[g]:
	#		print('{0}\t{1}'.format(e, g))


# Phytozome
overlaps = {}
M = {}
with open(args[2]) as inFl:
	for line in inFl:
		if line.startswith('#'):
			continue
		gff3Line = GFF3_line(line)
		if gff3Line.type == feat:
			scaf = gff3Line.seqid
			start = gff3Line.start
			end = gff3Line.end
			strand = gff3Line.strand
			gene_name = gff3Line.attributes[attr]

			if scaf in  overlaps:
				assert gene_name not in overlaps[scaf]
				overlaps[scaf][gene_name] = {strand:(start,end)}
			else:
				overlaps[scaf] = {gene_name:{strand:(start,end)}}

# MAKER
with open(args[1]) as inFl:
	for line in inFl:
		if line.startswith('#'):
			continue
		if line.startswith('>'):
			break
		gff3Line = GFF3_line(line)
		if gff3Line.type == 'gene':
			scaf = gff3Line.seqid
			start = gff3Line.start
			end = gff3Line.end
			strand = gff3Line.strand
			gene_id = gff3Line.attributes['ID']

			if scaf not in overlaps:
				continue
			for g in overlaps[scaf]:
				if strand in overlaps[scaf][g]:
					if Overlaps(overlaps[scaf][g][strand], (start,end)):
						if not gene_id in Map:
							continue
						for e in Map[gene_id]:
							print('{0}\t{1}'.format(e, g))
