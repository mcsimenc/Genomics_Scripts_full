#!/usr/bin/env python3

import sys


def help():
	print('''
		usage:
			gffCategorizeGenome.py -scafLen <path> -gff <path>


		description: Categorizes GFF3 content. Reports overlap stats to stderr

		-scafLens	<path>

		-gff		<path>

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


def annotateRepeatString(name):
	'''
	This is a function that assigns a string to one of many predefined repeat categories.
	Adapted from ~/scripts/repeats/summarize_repeat_masker_gff.py

	'''

	supershort_name = None

	lowercase_name = name.lower()

	if 'simple' in lowercase_name:
		short_name = 'Simple'
	elif 'satellite' in lowercase_name:
		short_name = 'Satellite'
	elif 'minisat' in lowercase_name:
		short_name = 'Microsatellite'
	elif 'low_complexity' in lowercase_name:
		short_name = 'Low_complexity'
	elif 'copia' in lowercase_name or 'shacop' in lowercase_name:
		short_name = 'Copia'
	elif 'gypsy' in lowercase_name or 'ogre' in lowercase_name:
		short_name = 'Gypsy'
	elif 'hat' in lowercase_name:
		short_name = 'hAT'
	elif 'helitron' in lowercase_name:
		short_name = 'Helitron'
	elif 'mariner' in lowercase_name or 'tc1' in lowercase_name:
		short_name = 'Mariner'
	elif 'mudr' in lowercase_name:
		short_name = 'MuDR'
	elif 'harb' in lowercase_name:
		short_name = 'Harbinger'
	elif 'penelope' in lowercase_name:
		short_name = 'Penelope'
	elif 'polinton' in lowercase_name:
		short_name = 'Polinton'
	elif 'piggybac' in lowercase_name:
		short_name = 'PiggyBac'
	elif 'trna' in lowercase_name:
		short_name = 'tRNA'
	elif 'rrna' in lowercase_name:
		short_name = 'rRNA'
	elif 'dada' in lowercase_name:
		short_name = 'DADA'
	elif 'sine' in lowercase_name:
		short_name = 'Other_SINE'
	elif 'enspm' in lowercase_name or 'cacta' in lowercase_name:
		short_name = 'EnSpm/CACTA'
	elif 'rtex' in lowercase_name:
		short_name = 'RTEX'
	elif 'rte' in lowercase_name:
		short_name = 'RTE'
	elif 'jock' in lowercase_name or 'cr1' in lowercase_name or 'crack' in lowercase_name or 'daphne' in lowercase_name:
		short_name = 'Jockey'
	elif 'line' in lowercase_name:
		short_name = 'Other_LINE'
	elif 'dirs' in lowercase_name:
		short_name = 'DIRS'
	elif 'bel' in lowercase_name:
		short_name = 'BEL'
	elif 'dna' in lowercase_name:
		short_name = 'Other_DNA_transposon'
	elif 'ltr' in lowercase_name or 'tto1' in lowercase_name or 'tnt1' in lowercase_name or 'tlc1' in lowercase_name or 'tcn1' in lowercase_name or 'frogger' in lowercase_name:
		short_name = 'Other_LTR_retrotransposon'
	elif 'l1' in lowercase_name or 'tx1' in lowercase_name:
		short_name = 'L1'
	elif 'l2' in lowercase_name:
		short_name = 'L2'
	elif 'erv' in lowercase_name:
		short_name = 'ERV'
	elif 'rep' in lowercase_name:
		short_name = 'REP'
	elif 'sola' in lowercase_name:
		short_name = 'SOLA'
	elif 'sat' in lowercase_name:
		short_name = 'Satellite'
	else:
		short_name = name
		supershort_name = 'Other'

	if not supershort_name == 'Other':
		supershort_name = short_name

	#return (short_name, supershort_name)
	return supershort_name


def categorizeRepeat(gffLine):

	if '\trepeatmasker\t' in line:
		annotAttr = ['Name','dfam_2.0_annotation','repbase_22.04_annotation']
	elif '\thmmer\t' in line:
		annotAttr = ['Name']
	elif '\trRNA\t' in line or '\ttRNA\t' in line:
		annotAttr = ['ID']
	else:
		annotAttr = ['dfam_2.0_annotation','repbase_22.04_annotation']

	
	annotations = {}

	for  attr in annotAttr:

		if attr in gffLine.attributes:
			attrVal = gffLine.attributes[attr]
			if attr == 'Name' and (attrVal.startswith('RM_') or attrVal.startswith('scf') or attrVal.startswith('deg')):
				continue
			if attrVal == 'None':
				continue
			else:
				annotation = annotateRepeatString(attrVal)
				annotations[attr] = annotation

	if len(annotations) == 0:
		annot = 'Unclassified'
	else:
		annotsSet = set(list(annotations.values()))

		if len(annotsSet) == 1:
			annot = annotsSet.pop()
		else:
			if 'Other' in annotsSet:
				annotsSet.remove('Other')

			if len(annotsSet) == 1:
				annot = annotsSet.pop()

			else:
				if annotsSet.issubset(set(['Simple','Low_complexity','Satellite','Microsatellite'])):
					annot = 'Low_complexity'

				elif annotsSet.issubset(set(['hAT','Helitron','Mariner','MuDR','Harbinger','Polinton','PiggyBac','DADA','EnSpm/CACTA','Other_DNA_transposon','SOLA'])):
					annot = 'Other_DNA_transposon'

				elif annotsSet.issubset(set(['tRNA','rRNA'])):
					annot = 'Other_RNA'

				elif annotsSet.issubset(set(['Gypsy','Copia','Penelope','Other_SINE','RTEX','RTE','Jockey','Other_LINE','DIRS','BEL','Other_LTR_retrotransposon','L1','L2','REP','ERV'])):
					annot = 'Other_retrotransposon'
				else:
					annot = 'Other'
	
	if annot in ['Simple','Low_complexity','Satellite','Microsatellite']:
		return 'Simple_repeat'
	if annot in ['rRNA', 'tRNA', 'Other_RNA']:
		return 'RNA_gene'
	else:
		return 'TE'





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

#if len(sys.argv) < 3 or '-h' in args:
#	help()


pos = 0
start = None
end = None
gap = 0
uncategorized = 0
categorization = {'Protein_gene':0, 'RNA_gene':0, 'TE':0, 'Simple_repeat':0, 'Repeat':0}
last_category = None
last_strand = None
last_line = None

for line in sys.stdin:

	if not line.startswith('#'):

		category = FeatType(line)


		if not category == None: # All lines except those matching FeatType are ignored b/c they are nested subordinate features.

			gffLine = GFF3_line(line)

			if category == 'Repeat':
				category = categorizeRepeat(gffLine)

			strand = gffLine.strand
			start = int(gffLine.start)
			end = int(gffLine.end)
			length = end - start + 1
			gap = start-pos
			
			if gap >= 0: # No overlap. Add gap to uncategorized, length to category, and continue

				uncategorized += gap
				pos = end + 1
				#categorization[category] += length

			elif gap < 0: # Overlap. Report overlap length and categories.

				overlap = gap
				if last_strand == strand:
					print('{0}\t{1}\t{2}\t{3}\tOverlap:{4}\tLen1:{5}\tLen2:{6}'.format(last_strand, strand, last_category, category, abs(overlap), last_length, length), file=sys.stderr)
					print('{0}\t{1}'.format(GFF3_line(last_line).attributes_str, gffLine.attributes_str), file=sys.stderr)
					print('############', file=sys.stderr)
				if end <= pos:
					#print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(last_strand, strand, last_category, category, GFF3_line(last_line).attributes_str, gffLine.attributes_str))
					if last_strand == strand:
						print('{0}\t{1}\t{2}\t{3}\tOverlap:{4}\tLen1:{5}\tLen2:{6}'.format(last_strand, strand, last_category, category, abs(overlap), last_length, length), file=sys.stderr)
						print('{0}\t{1}'.format(GFF3_line(last_line).attributes_str, gffLine.attributes_str), file=sys.stderr)
						print('############', file=sys.stderr)
					#print('End {0}\tPos{1}'.format(end, pos))
				elif end > pos:
					pos = end + 1

				
			last_category = category
			last_strand = strand
			last_line = line
			last_length = length
