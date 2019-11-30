#!/usr/bin/env python3

import sys


def help():
	print('''
		usage:
			gffReportUnannotatedAmount.py -scafLens <path> -gff <path>


		description: Reports amount of each scaffold that has no annotation on either strand.

		-scafLens	<path>	Lengths of sequences in GFF. Two columns, seqname and length

		-gff		<path> 	GFF3 file

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



def FeatType(line):
	if '\tmaker\t' in line and '\tgene\t' in line and not 'trnascan' in line:
		return 'Protein_gene'
	elif '\tmaker\t' in line and '\tgene\t' in line and 'trnascan' in line:
		return 'RNA_gene'
	elif '\trepeatmasker\t' in line and '\tmatch\t' in line:
		return 'Repeat'
	elif '\tLTRharvest\t' in line and '\trepeat_region\t' in line:
		return 'TE'
	elif '\thmmer\t' in line and '\ttandem_repeat\t' in line:
		return 'Simple_repeat'
	elif '\tRNAmmer\t' in line and '\trRNA\t' in line:
		return 'RNA_gene'
	else:
		return None

args =sys.argv

if len(sys.argv) < 5 or '-h' in args:
	help()


last_end = 0
gap = 0
uncategorized = 0
start = None
end = None
scaf = None

with open(sys.argv[sys.argv.index('-scafLens') + 1]) as scafLensFl:
	scafLens = {}
	for line in scafLensFl:
		scaffold, length = line.strip().split()
		if scaffold in scafLens:
			scafLens[scaffold] += int(length)
		else:
			scafLens[scaffold] = int(length)

with open(sys.argv[sys.argv.index('-gff')+1]) as gffFl:

	for line in gffFl:

		if not line.startswith('#'):

			category = FeatType(line)

			if not category == None: # All lines except those matching FeatType are ignored b/c they are nested subordinate features.

				gffLine = GFF3_line(line)
				strand = gffLine.strand
				start = int(gffLine.start)
				end = int(gffLine.end)
				length = end - start + 1
				gap = start-last_end -1

				if gffLine.seqid != scaf and scaf != None:
					if last_end > scafLens[scaf]:
						sys.exit("Last feature on scaffold beyond end of scaffold, scaffold: {0}".format(scaf))
					if last_end == scafLens[scaf]:
						pass
					if last_end < scafLens[scaf]:
						uncategorized += scafLens[scaf] - last_end

					print('{0}\t{1}'.format(scaf, uncategorized))
					uncategorized = 0
					last_end = 0
					
				scaf = gffLine.seqid

				if gap >= 0: # No overlap. Add gap to uncategorized, length to category, and continue

					uncategorized += gap
					last_end = end
					#categorization[category] += length

			else:
					continue

if last_end-1 > scafLens[scaf]:
	sys.exit("Last feature on scaffold beyond end of scaffold, scaffold: {0}".format(scaf))
if last_end-1 == scafLens[scaf]:
	pass
if last_end-1 < scafLens[scaf]:
	uncategorized += scafLens[scaf] - last_end

print('{0}\t{1}'.format(scaf, uncategorized))
