#!/usr/bin/env python3

import sys

def help():
	print('''
			usage:
				addLTRharvestAnnotationsIfPossible.py -dfam <filepath> -repbase  <filepath> < input.gff 1> output.gff 2>changedLines.report.txt


			description: Tries to update GFF with LTRharvest annotations that lost information due to maker truncating seq headers in repeat library

				Input -dfam and -repbase files should be two-column and look like this:

					scf7180000007563_(dbseq-nr_1)_[1350599,1353840]	Copia1-I_DM

				In the input gff the Target attribute should look like this:

					Target=species:scf7180000010242|genus:Unspecified 6980 7045 +


				This script parses the -dfam and -repbase input and calculates the length of each feature based on the
				[int, int] part of the first column. When going through the input gff it parses the numbers at the end
				of the target attribute and takes the largest one to be the minimum length of the sequence it is derived
				from in the repeat library. It looks through the parsed -dfam and -repbase for that scaffold and if it 
				finds only one length that fits the minimum length of the feature then the annotation is used for that one.

			


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


def parseAnnot(annotFlpath):
	# Example input from annotFlpath
	#scf7180000007563_(dbseq-nr_1)_[1350599,1353840]	Copia1-I_DM
	#
	# Output:
	# { scaf1:{len1:annot, len2:annot, ...}, scaf2:{...} }
	outputDct = {}
	with open(annotFlpath) as inFl:
		for line in inFl:
			if not line=='\n':
				seq, annot = line.strip().split('\t')
				seqSplit = seq.split('_')
				scaf = seqSplit[0]
				coords = seqSplit[-1].lstrip('[').rstrip(']').split(',')
				length = int(coords[1])-int(coords[0])+1
				if scaf in outputDct:
					outputDct[scaf][length] = annot
				else:
					outputDct[scaf] = {length:annot}

	return outputDct


def getAnnot(annotDct, scaf, minLength):
	if scaf not in annotDct:
		return None
	else:
		if len(annotDct[scaf]) == 1:
			return list(annotDct[scaf].values())[0]
		else:
			foundSeq = False
			foundAnnot = None
			for seqLen in annotDct[scaf]:
				if minLength <= int(seqLen):
					if foundSeq == True:
						return None
					foundSeq = True
					foundAnnot = annotDct[scaf][seqLen]
			return foundAnnot


	

args = sys.argv



DfamAnnotDct = parseAnnot(args[args.index('-dfam')+1])
RepbaseAnnotDct = parseAnnot(args[args.index('-repbase')+1])

for line in sys.stdin:
	if line.startswith('#'):
		print(line, end='')
		continue

	gffLine = GFF3_line(line)
	if gffLine.attributes['Target'].startswith('species:scf') or gffLine.attributes['Target'].startswith('species:deg'):

		target = gffLine.attributes['Target'].lstrip('species').lstrip(':').rstrip(' +').rstrip(' -').split('|genus:Unspecified ')
		scaf = target[0]
		coords = [int(i) for i in target[1].split( ) ]
		minLength = max(coords)
		if gffLine.attributes['Dfam_2.0_annotation'] == 'None':
			newAnnot = getAnnot(DfamAnnotDct, scaf, minLength)
			if newAnnot != None:
				gffLine.attributes['Dfam_2.0_annotation'] = newAnnot


		if gffLine.attributes['Repbase_22.04_annotation'] == 'None':
			newAnnot = getAnnot(RepbaseAnnotDct, scaf, minLength)
			if newAnnot != None:
				gffLine.attributes['Repbase_22.04_annotation'] = newAnnot

		gffLine.refreshAttrStr()
		print(str(gffLine))
		print(str(gffLine), file=sys.stderr)

	else:
		print(line, end='')




#Sacu_v1.1_s0001	repeatmasker	match	14961	15030	313	+	.	ID=Sacu_v1.1_s0001:hit:109:1.3.0.0;Name=species:scf7180000010242|genus:Unspecified;Target=species:scf7180000010242|genus:Unspecified 6980 7045 +;Dfam_2.0_annotation=None;Repbase_22.04_annotation=None


