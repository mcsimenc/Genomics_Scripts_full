#!/usr/bin/env python3


#Process bedtools output so each feature has its classification and report:

#ID, strand, classification, ID2, strand2, classification


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
					annot = 'DNA_transposon'

				elif annotsSet.issubset(set(['tRNA','rRNA'])):
					annot = 'RNA_gene'

				elif annotsSet.issubset(set(['Penelope','Other_SINE','RTEX','RTE','Jockey','Other_LINE','DIRS','BEL','Other_LTR_retrotransposon','L1','L2','REP','ERV'])):
					annot = 'Other_RNA_transposon'
				elif annotsSet.issubset(set(['Gypsy'])):
					annot = 'Gypsy'
				elif annotsSet.issubset(set(['Copia'])):
					annot = 'Copia'
				else:
					#annot = 'Other repetetive'
					annot = '_'.join(list(annotsSet))
	return annot
	#if annot in ['Simple','Low_complexity','Satellite','Microsatellite']:
	#	return 'Simple_repeat'
	#if annot in ['rRNA', 'tRNA', 'Other_RNA']:
	#	return 'RNA_gene'
	#else:
	#	return 'TE'





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

def Overlap(A,B):
	'''
	takes two tuples and outputs two tuples, which will be identical if the original overlap otherwise will be the originals

	let A = (a1, a2), B = (b1, b2) | a1<=b1, a1<=a2, b1<=b2

	case 1: a2<=b1 ---> no overlap

	case 2: b1<a2 && b2>a2 ---> overlap

	case 3: b2<=a2 ---> overlap == len(b)
	'''

	if min(A) > min(B):
		C=A
		A=B
		B=C
	assert min(A) <= min(B), "tupes given to overlap() in wrong order: A={0}, B={1}".format(A,B)

	if min(B) >= max(A): # no overlap
		return 0
	elif min(B) < max(A) and max(B) > max(A): # overlap 
		output = (min(A),max(B))
		return max(A)-min(B) + 1
	elif max(B) <= max(A):
		return max(B) - min(B) + 1
	else:
		raise Exception("Unexpected result from overlap(A,B) using A={0}, B={1}".format(A,B))
args =sys.argv

#if len(sys.argv) < 3 or '-h' in args:
#	help()


for line in sys.stdin:

	if not line.startswith('#'):


		contents = line.strip().split('\t')
		attr1 = contents[9]
		attr2 = contents[19]
		strand1 = contents[5]
		strand2 = contents[15]
		start1 = int(contents[1])
		start2 = int(contents[11])
		end1 = int(contents[2])
		end2 = int(contents[12])
		seqid1 = contents[0]
		seqid2 = contents[10]
		
		gffStr1 = '{4}\t.\t.\t{0}\t{1}\t{2}\t.\t.\t{3}'.format(start1, start1, strand1, attr1, seqid1)
		gffStr2 = '{4}\t.\t.\t{0}\t{1}\t{2}\t.\t.\t{3}'.format(start2, start2, strand2, attr2, seqid2)

		gffLine1 = GFF3_line(gffStr1)
		gffLine2 = GFF3_line(gffStr2)

		length1 = end1-start1+1
		length2 = end2-start2+1

		overlap = Overlap((start1,end1),(start2, end2))

#Azfi_s4737	manual	scaffold	3160	3226	.	.	.	ID=Azfi_s4737

#Azfi_s0003	10039205	10046228	LTR_retrotransposon1263	.	-	LTRharvest	LTR_retrotransposon	.	ID=LTR_retrotransposon1263;Parent=repeat_region1263;ltr_similarity=95.47;seq_number=2;dfam_2.0_annotation=Gypsy-168-I_DR;repbase_22.04_annotation=Gypsy-3_SMo-I_Gypsy_Selaginella_moellendorffii	Azfi_s0003	10041640	10041734	Azfi_s0003:hit:18023:1.3.0.100	863	-	repeatmasker	match	.	ID=Azfi_s0003:hit:18023:1.3.0.100;Name=scf7180000009490|quiver_1972_2065_+;dfam_2.0_annotation=None;repbase_22.04_annotation=Gypsy-55_AA-I_Gypsy_Aedes_aegypti


		category1 = categorizeRepeat(gffLine1)
		category2 = categorizeRepeat(gffLine2)

		ID1 = attr1.split(';')[0]
		ID2 = attr2.split(';')[0]

		if strand1 == strand2:

			# Print anything that overlaps a gene
			if gffLine1.attributes['ID'].startswith('{0}.g'.format(gffLine1.seqid)) and gffLine2.attributes['ID'].startswith('{0}.g'.format(gffLine2.seqid)): # Both are genes
				sys.exit('Two genes overlap on same strand:	{0}	{1}'.format(gffLine1.attributes['ID'], gffLine2.attributes['ID']))
			elif gffLine1.attributes['ID'].startswith('{0}.g'.format(gffLine1.seqid)) and not gffLine2.attributes['ID'].startswith('{0}.g'.format(gffLine2.seqid)): # 1 is gene
				print('{0}\toverlaps gene'.format(gffLine2.attributes['ID']))
				continue
			elif not gffLine1.attributes['ID'].startswith('{0}.g'.format(gffLine1.seqid)) and gffLine2.attributes['ID'].startswith('{0}.g'.format(gffLine2.seqid)): # 2 is gene
				print('{0}\toverlaps gene'.format(gffLine1.attributes['ID']))
				continue

			#Azfi_s0280.g062279
			
			# Print anything that overlaps LTRharvest
			if gffLine1.attributes['ID'].startswith('LTR_retrotransposon') and gffLine2.attributes['ID'].startswith('LTR_retrotransposon'):
				sys.exit('Two LTRharvest overlap on same strand:	{0}	{1}'.format(gffLine1.attributes['ID'], gffLine2.attributes['ID']))
			elif gffLine1.attributes['ID'].startswith('LTR_retrotransposon') and not gffLine2.attributes['ID'].startswith('LTR_retrotransposon'):
				print('{0}\toverlaps LTRharvest'.format(gffLine2.attributes['ID']))
				continue
			elif not gffLine1.attributes['ID'].startswith('LTR_retrotransposon') and gffLine2.attributes['ID'].startswith('LTR_retrotransposon'):
				print('{0}\toverlaps LTRharvest'.format(gffLine1.attributes['ID']))
				continue

			# Print if overlaps tRNAscan
			if gffLine1.attributes['ID'].startswith('trnascan') and gffLine2.attributes['ID'].startswith('trnascan'):
				sys.exit('Two tRNAscan overlap on same strand:	{0}	{1}'.format(gffLine1.attributes['ID'], gffLine2.attributes['ID']))
			elif gffLine1.attributes['ID'].startswith('trnascan') and not gffLine2.attributes['ID'].startswith('trnascan'):
				print('{0}\toverlaps tRNAscan'.format(gffLine2.attributes['ID']))
				continue
			elif not gffLine1.attributes['ID'].startswith('trnascan') and gffLine2.attributes['ID'].startswith('trnascan'):
				print('{0}\toverlaps tRNAscan'.format(gffLine1.attributes['ID']))
				continue


			# Print shortest
			if length1<length2:
				print('{0}\tshorter'.format(gffLine1.attributes['ID']))
				#print(attr2.split(';')[0])
			else:
				print('{0}\tshorter'.format(gffLine2.attributes['ID']))
				#print(attr1.split(';')[0])
		#	if 'trnascan' in ID1 and 'trnascan' in ID2:
		#		if length1<length2:
		#			print(ID1)
		#		else:
		#			print(ID2)
		#	elif 'trnascan' in ID1:
		#		print(ID2)
		#	elif 'trnascan' in ID2:
		#		print(ID1)
		#	else:
		#		if length1<length2:
		#			print(ID1)
		#		else:
		#			print(ID2)
				
			#print(overlap, "SAME",length1, category1, category2, length2)
			#print()
			#print(line)
		else:
			pass
			#print(overlap, "DIFFERENT", length1, category1, strand1, strand2, category2, length2)
