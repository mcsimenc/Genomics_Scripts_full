#!/usr/bin/env python3

# MAKER assigns most repeats + strand by default by design. This script updates the strand based on how I did the repeat classification.
# Elements with a value for the attribute dfam_annotation != None get assigned the strand they already have because I did not search dfam on the reverse compliment of repeat features.
# Elements with a value for the attribute repbase_annotation != None get assigned the strand in the corresponding repbase best blast hit output
# Elements with a classification of Simple, Satellite, and Low complexity get assigned . to indicate strandlessness (both strands)

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


annotAttr = ['Name','dfam_2.0_annotation','repbase_22.04_annotation']


strands = {}
with open(sys.argv[1]) as strandFl:
	for line in strandFl:
		contents = line.strip().split()
		strands[contents[0]] = contents[2]

strands_RMlib= {}
with open(sys.argv[2]) as strandFl:
	for line in strandFl:
		contents = line.strip().split()
		strands_RMlib[contents[0]] = contents[2]
		
for line in sys.stdin:
	if not line.startswith('#'):
		gffLine = GFF3_line(line)
		if gffLine.source == 'repeatmasker':
			ID = gffLine.attributes['ID']
			annotations = {}
			for  attr in annotAttr:
				attrVal = gffLine.attributes[attr]
				annotations[attr] = annotateRepeatString(attrVal)

			annotsSet = set(list(annotations.values()))
			#for item in annotations:
			#	annot = annotations[item]
			abbreviatedAnnotsSet = set()
			for name in annotsSet:

				if name == 'Copia':
					abbreviatedAnnotsSet.add('Copia')
				elif name == 'Gypsy':
					abbreviatedAnnotsSet.add('Gypsy')
				elif name in ['Other','Unclassified']:
					abbreviatedAnnotsSet.add('Other')
				elif name in ['Unclassified']:
					abbreviatedAnnotsSet.add('Unclassified')
				elif name in ['Simple','Low_complexity','Satellite','Microsatellite']:
					abbreviatedAnnotsSet.add('Simple')
				elif name in ['hAT','Helitron','Mariner','MuDR','Harbinger','Polinton','PiggyBac','DADA','EnSpm/CACTA','Other_DNA_transposon','SOLA']:
					abbreviatedAnnotsSet.add('DNAtransposon')
				elif name in ['Penelope','Other_SINE','RTEX','RTE','Jockey','Other_LINE','DIRS','BEL','Other_LTR_retrotransposon','L1','L2','REP','ERV']:
					abbreviatedAnnotsSet.add('OtherRetrotransposon')
				elif name in ['tRNA','rRNA']:
					abbreviatedAnnotsSet.add('RNA')
				else:
					print(annot+' not accounted for', file=sys.stderr)
					sys.exit()
			if len(abbreviatedAnnotsSet) == 1:
				annot = abbreviatedAnnotsSet.pop()
			else:
				if 'Other' in abbreviatedAnnotsSet:
					abbreviatedAnnotsSet.remove('Other')

				if len(abbreviatedAnnotsSet) == 1:
					annot = abbreviatedAnnotsSet.pop()

				else:
					if abbreviatedAnnotsSet == set(list(['Gypsy', 'Copia'])):
						annot = 'OtherRetrotransposon'
					elif abbreviatedAnnotsSet == set(list(['OtherRetrotransposon', 'Copia'])):
						annot = 'OtherRetrotransposon'
					elif abbreviatedAnnotsSet == set(list(['Gypsy', 'OtherRetrotransposon'])):
						annot = 'OtherRetrotransposon'
					elif abbreviatedAnnotsSet == set(list(['Gypsy', 'OtherRetrotransposon', 'Copia'])):
						annot = 'OtherRetrotransposon'
					else:
						annot = 'Other'


			if annot in ['Simple', 'Satellite', 'Microsatellite', 'Low_complexity']:
				gffLine.strand = '.'
				#print('changed via simple/sat/low complexity', file=sys.stderr)
			elif annot == 'Other':
				print('Annot = Other', file=sys.stderr)
				print(line.strip().split()[-1], file=sys.stderr)
				print(file=sys.stderr)
				gffLine.strand = '?'
			else:
				try:
					gffLine.strand = strands[ID] # Check imported database
					#print('changed via tblastx 2 repbase', file=sys.stderr)
				except KeyError:
					if gffLine.attributes['dfam_2.0_annotation'] != 'None':
						gffLine.strand = '+' # Automatically assign + if it has a Dfam annot because that was done only for the plus strand
						#print('changed via dfam', file=sys.stderr)
					elif gffLine.attributes['Name'].startswith('RM'):
						try:
							name = '_'.join(gffLine.attributes['Name'].split('_')[:-3])
							gffLine.strand = strands_RMlib[name]
							#print('Success!', file=sys.stderr)
						except KeyError:
							gffLine.strand = '?'
							#print('Failure!', file=sys.stderr)
							#print(line, end='', file=sys.stderr)
					else:
						gffLine.strand = '?'
						#print(line, end='', file=sys.stderr)
						#print('could not change strand: {0}, annot={1}'.format(ID, annot), file=sys.stderr)
		print(str(gffLine))
	else:
		print(line, end='')







#Sacu_v1.1_s3778	hmmer	tandem_repeat	2901	3076	.	.	.	ID=Sacu_CentromericRepeat_08259;Name=Satellite_centromeric_repeat
####
#Sacu_v1.1_s3778	hmmer	tandem_repeat	3078	3895	.	.	.	ID=Sacu_CentromericRepeat_08260;Name=Satellite_centromeric_repeat
####
#Sacu_v1.1_s3779	repeatmasker	match	2	3866	3.06e+04	+	.	ID=Sacu_v1.1_s3779:hit:96265:1.3.0.0;Name=scf7180000009972_2049_5936_+;dfam_2.0_annotation=None;repbase_22.04_annotation=None
####
#Sacu_v1.1_s3780	repeatmasker	match	3	3394	2.65e+04	+	.	ID=Sacu_v1.1_s3780:hit:115461:1.3.0.0;Name=RM_9664_rnd-4_family-330_5865_9267_+;dfam_2.0_annotation=None;repbase_22.04_annotation=REP-6_LMi_Transposable_Element_Locusta_migratoria
####
#Sacu_v1.1_s3781	RNAmmer-1.2	rRNA	7	2918	2.29e+03	+	.	ID=28s_rRNA_0298
####
#
#
#
