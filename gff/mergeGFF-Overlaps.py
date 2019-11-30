#!/usr/bin/env python3

import sys

if '-h' in sys.argv:
	print('''
 usage:
 	mergeGFF-Overlaps.py < file.gff > output.gff
 
 
 description: removes score and attributes from GFF3 input
 	     and combines any overlapping features. Strand
 	     is ignored.
 
 	     -keepAttr	keep the attribute column as is

		''')
	sys.exit()

class GFF3_line:

	'''

	Attributes:
			field0, ... , field8 - string
			attributes - dictionary

	Methods:    line() - returns tab-sep fields for printing/writing

	'''

	def __init__(self, line, **kwargs):

		(self.seqid, self.source, self.type, self.start, self.end, self.score, self.strand, self.phase, self.attributes_str) = line.strip().split('\t')
		
		self.line_number = None

		if 'line_number' in kwargs:	

			self.line_number = kwargs['line_number']

		attributes_list = self.attributes_str.split(';')

		self.attributes = { attr.split('=')[0]:attr.split('=')[1] for attr in attributes_list }

		# rename the name attribute so it conforms to GFF3 specifications, where Name is a reserved attribute key. The version of LTRDigest makes attribute key name
		if 'name' in self.attributes:

			self.attributes['Name'] = self.attributes.pop('name')

	def __repr__(self): # for when str() or repr() are called

		return '\t'.join( [ str(self.seqid), str(self.source), str(self.type), str(self.start), str(self.end), str(self.score), str(self.strand), str(self.phase), str(self.attributes_str) ] )




def mergeCoords(A,B):
	'''
	takes two tuples and outputs two tuples, which will be identical if the originals overlap otherwise will be the originals

	let A = (a1, a2), B = (b1, b2) | a1<=b1, a1<=a2, b1<=b2

	case 1: a2<=b1 ---> output originals

	case 2: b1<a2 && b2>a2 ---> output (a1, b2)

	case 3: b2<=a2 ---> output A
	'''

	assert min(A) <= min(B), "tuples given to mergeCoords in wrong order: A={0}, B={1}".format(A,B)

	if min(B) > max(A):
		return ((A,B), 0)
	elif min(B) <= max(A) and max(B) > max(A):
		output = (min(A),max(B))
		return ((output, output), 1)
	elif max(B) <= max(A):
		return ((A,A), 2)
	else:
		raise Exception("Unexpected result from mergeCoords(A,B) using A={0}, B={1}".format(A,B))


gffFeats = {}

for line in sys.stdin:
	if not line.startswith('#'):

		lineObj = GFF3_line(line)
		scaf = lineObj.seqid
		#(self.seqid, self.source, self.type, self.start, self.end, self.score, self.strand, self.phase, self.attributes_str) = line.strip().split('\t')
		#attributes_list = self.attributes_str.split(';')
		#self.attributes = { attr.split('=')[0]:attr.split('=')[1] for attr in attributes_list }

		if scaf in gffFeats:
			gffFeats[scaf].append(lineObj)
		else:
			gffFeats[scaf] = [lineObj]

for scaf in gffFeats: # sort features by start coordinate then merge overlapping features
	gffFeats[scaf] = sorted(gffFeats[scaf], key=lambda x:int(x.start))
	newScafFeats = []
	currentFeat = gffFeats[scaf][0]
	i=0

	while i< len(gffFeats[scaf])-1:

		nextFeat = gffFeats[scaf][i+1]
		mergeResult = mergeCoords( (int(currentFeat.start), int(currentFeat.end)), (int(nextFeat.start), int(nextFeat.end)) )

		if mergeResult[1] == 0: # feats do not overlap

			currentFeat.start, currentFeat.end = mergeResult[0][0]
			currentFeat.score = '.'
			if '-keepAttr' not in sys.argv:
				currentFeat.attributes_str = '.'
			newScafFeats.append(currentFeat)
			currentFeat = nextFeat

		elif mergeResult[1] == 1: # feats overlap case 1
			currentFeat.start, currentFeat.end = mergeResult[0][0]

		elif mergeResult[1] == 2: # feats overlap case 2
			currentFeat.start, currentFeat.end = mergeResult[0][0]

		else:
			raise Exception("Unexpected result from mergeResult block")

		i += 1

	currentFeat.score = '.'
	currentFeat.attributes_str = '.'
	newScafFeats.append(currentFeat)
	gffFeats[scaf] = newScafFeats
	
for scaf in sorted(gffFeats.keys()):
	for line in gffFeats[scaf]:
		print(str(line))
