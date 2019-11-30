#!/usr/bin/env python3

import sys

def help():
	print('''
			usage:
				gffCheckOverlaps.py [options] < input.gff > output


			description: 
				prints GFF lines of features that have exact duplicates except for
				the highest scoring feature.

			options:



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

args =sys.argv
if '-h' in args or '-help' in args:
	help()

coordsDct = {}
for line in sys.stdin:
	if not line.startswith('#'):
		gffLine = GFF3_line(line)
		coords = (gffLine.start,gffLine.end)
		if gffLine.seqid in coordsDct:
			if coords in coordsDct[gffLine.seqid]:
				coordsDct[gffLine.seqid][coords].append(gffLine)
			else:
				coordsDct[gffLine.seqid][coords] = [gffLine]
		else:
			coordsDct[gffLine.seqid] = {coords:[gffLine]}

for scaf in sorted(list(coordsDct.keys())):
	for coord in coordsDct[scaf]:
		if len(coordsDct[scaf][coord]) > 1:
			highScore = float('-inf')
			highScoreIndex = 0
			# Find highest scoring duplicate
			for i in range(len(coordsDct[scaf][coord])):
				gffLine = coordsDct[scaf][coord][i]
				if float(gffLine.score) > highScore:
					highScoreIndex = i
			# Print all except highest scoring duplicate
			for i in range(len(coordsDct[scaf][coord])):
				gffLine = coordsDct[scaf][coord][i]
			#	if i == highScoreIndex:
			#		continue
			#	else:
			#		print(str(gffLine))
				print(str(gffLine))
