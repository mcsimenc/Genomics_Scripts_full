#!/usr/bin/env python3

#from reportAnnotChange import annotateRepeatString
#import reportAnnotChange as A
import sys
import re

def annotateRepeatString(Str, start=None, end=None, bed=False):
	'''
	This is a function that assigns a string to one of many predefined repeat categories.
	Adapted from ~/scripts/repeats/summarize_repeat_masker_gff.py

	input ->  a string Str, an int start, and an int end. start and end are optional.
	output -> a tuple:  (str, str, int)
			    (annot, shortAnnot, supershortAnnot, length)

			    annot -> raw annot extracted from Str using regex
			    shortAnnot -> predefined annotations, if string does not fit into one of these it is simply reported here
			    supershortAnnot -> same as shortAnnot, but unknow strings are categorized as 'other'
			    length -> the length of the feature, if start and end are provided

	if bed=True, treat the length calculation as bed format (0-based)
	'''

	target_re_pattern = re.compile('Target "Motif:(.+)"')
	target_re_pattern_repeatmasker = re.compile('Target=(.+?)\s') # Matches repeatmasker and repeatrunner lines in maker gff
	name_simple_pattern = re.compile('\([ATCG]+\)n')
	target_re_pattern_makerlines = re.compile('Name=species:(.+?)\|genus')
	bestblasthit_pat = re.compile('bestblasthit_(.+)\.aln_len')

	if start==None or end==None:
		length = 'NA'
	else:
		if bed == True:

			length = int(end) - int(start)

		else: # Gff input
			length = int(end) - int(start) + 1

	if 'bestblast' in Str:
		name = re.search(bestblasthit_pat, Str).group(1)
	elif 'genus:Simple' in Str:
		name = 'Simple'
	else:
		#name = re.search(target_re_pattern_makerlines, Str).group(1)
		try:
			name = re.search(target_re_pattern, Str).group(1)
		except AttributeError:
			try:
				name = re.search(target_re_pattern_repeatmasker, Str).group(1)
			except AttributeError:
				name = re.search(target_re_pattern_makerlines, Str).group(1)


	supershort_name = None

	lowercase_name = name.lower()

	if re.search(name_simple_pattern, name):
		short_name = 'Simple'
	elif name == 'Simple':
		short_name = 'Simple'
	elif name == 'Unspecified':
		short_name = 'Unspecified'
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
	elif 'dna-' in lowercase_name or re.search('dna\d', lowercase_name):
		short_name = 'Other_DNA_transposon'
	elif 'ltr' in lowercase_name or 'tto1' in lowercase_name or 'tnt1' in lowercase_name or 'tlc1' in lowercase_name or 'tcn1' in lowercase_name:
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
	elif 'minisat' in lowercase_name:
		short_name = 'Microsatellite'
	elif 'unspecified' in lowercase_name:
		short_name = 'Unspecified'
	else:
		short_name = name
		supershort_name = 'Other'

	if not supershort_name == 'Other':
		supershort_name = short_name

	return (name, short_name, supershort_name, length)


# For bedtools intersect -wa -wb
#with open(sys.argv[1]) as inFl:
#	for line in inFl:
#		line = line.split('\t')
#		start = line[1]
#		end = line[2]
#		attr = line[9]
#		newAttr = line[19]
#		#print(line, file=sys.stderr)
#		origAnnot = annotateRepeatString(attr, start, end, bed=True)
#		newAnnot = annotateRepeatString(newAttr, bed=True)
#		print(origAnnot[2], newAnnot[2], origAnnot[3])

# For bedtools subtract v1.1-v1.2
with open(sys.argv[1]) as inFl:
	for line in inFl:
		line = line.split('\t')
		start = line[1]
		end = line[2]
		attr = line[9]
		#newAttr = line[19]
		#print(line, file=sys.stderr)
		origAnnot = annotateRepeatString(attr, start, end, bed=True)
		#newAnnot = annotateRepeatString(newAttr, bed=True)
		newAnnot = "NongeneNonrpt"
		print(origAnnot[2], newAnnot, origAnnot[3])

# For bedtools subtract v1.2-v1.1
#with open(sys.argv[1]) as inFl:
#	for line in inFl:
#		line = line.split('\t')
#		start = line[1]
#		end = line[2]
#		attr = line[9]
#		#newAttr = line[19]
#		#print(line, file=sys.stderr)
#		newAnnot = annotateRepeatString(attr, start, end, bed=True)
#		origAnnot = 'NongeneNonrpt'
#		print(origAnnot, newAnnot[2], newAnnot[3])

# For BED of full annotation
#with open(sys.argv[1]) as inFl:
#	for line in inFl:
#		line = line.split('\t')
#		start = line[1]
#		end = line[2]
#		attr = line[9]
#		#newAttr = line[19]
#		#print(line, file=sys.stderr)
#		annot = annotateRepeatString(attr, start, end, bed=False)
#		print(annot[2] + '\t' +  str(annot[3]))
