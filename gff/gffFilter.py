#!/usr/bin/env python3

import sys
import re

def help():
	print('''
	Usage:
	------------
	gffFilter.py [options] < input.gff > output.gff

	Description:
	------------
	Retains or removes features in input.gff. Currently you can only use -scaf OR -id

	Options:
	------------
	-scaf <path>	Output scafs from the fasta in the file at <path>

	-id <path>	Select features whose ID attribute matches something in the file at <path>

	-v		Invert. Print non-matching lines.
	''')
	sys.exit(0)


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

if '-h' in args or '-help' in args or len(args) < 3:
	help()



if '-id' in args:
	IDpth = args[args.index('-id') + 1]
	IDset = set()
	ID = True

	with open(IDpth) as IDfl:
		for line in IDfl:
			IDset.add(line.strip())

else:
	ID = False


if '-scaf' in args:
	Scafpth = args[args.index('-scaf') + 1]
	Scafset = set()
	SCAF = True

	with open(Scafpth) as Scaffl:
		for line in Scaffl:
			Scafset.add(line.strip())

else:
	SCAF = False


if SCAF and ID:
	print('You used both -scaf and -id but only -id will be used. No implementation exists for both.', file=sys.stderr)


for line in sys.stdin:
	if line.startswith('#'):
		print(line, end='')
		continue

	gffLine = GFF3_line(line)

	if ID:
		if gffLine.attributes['ID'] in IDset:
			if '-v' in args:
				continue
			else:
				print(line, end='')

		else:
			if '-v' in args:
				print(line, end='')
			else:
				continue

	elif SCAF:
		if gffLine.seqid in Scafset:
			if '-v' in args:
				continue
			else:
				print(line, end='')

		else:
			if '-v' in args:
				print(line, end='')
			else:
				continue

