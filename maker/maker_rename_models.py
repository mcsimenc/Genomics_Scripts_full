#!/usr/bin/env python3


import sys
import re

def help():
	print('''
		Usage:
		------------
		maker_rename_models.py <maker.gff> [-p <prefix>] > maker.renamed.gff 2> model_map.txt


		Description:
		------------
		Renames gene models and subordinate features to the form:

			<prefix>_<scaffold>.<model>

		where <prefix> is give as the second argument to the script call,
		<scaffold> is the name of the scaffold the feature resides on, and
		the first <model> is g000000 or g<int> if -basenum is supplied, with
		each subsequent model incremented by 1. If <prefix> is not supplied
		then the new model name will be:

			<scaffold>.<model>

		A GFF with new names is written to stdout and a two-column file
		mapping old to new names is written to stderr
		
		Options:
		------------
		-p <string>	Prefix for all model names.

		-basenum <int>	Number for first <model>. Will be expanded with leading
				zeroes up to 6 digits.

		''')
	sys.exit(0)


args = sys.argv

if '-h' in args or '-help' in args or len(args) < 2:
	help()

inflpth = args[1]

if '-p' in args:
	prefix = args[args.index('-p')+1]
else:
	prefix = ''

if '-basenum' in args:
	modelnum = int(args[args.index('-basenum')+1])
else:
	modelnum = 0


lastmodel = ''

with open(inflpth) as infl:

	for line in infl:

		if '\tgene\t' in line:

			modelnum += 1
			scaf = line.split('\t')[0]
			genemodel = 'g' + str(modelnum).zfill(6)

			if prefix == '':
				model = '{0}.{1}'.format(scaf, genemodel)
			else:
				model = '{0}_{1}.{2}'.format(prefix, scaf, genemodel)

			ID_match = re.search('ID=(.+);', line)
			# remember this gene model's name to check if other features are in proper order. the input gff is expected to be sorted such that subordinate features directly follow their parent gene feature and before the next gene feature. 
			lastmodel = ID_match.group(1)
			ID_span = ID_match.span(1)
			Name_match = re.search('Name=(.+)$', line)
			Name_span = Name_match.span(1)
			newline = '{0}{1}{2}{1}{3}'.format(line[:ID_span[0]], model, line[ID_span[1]:Name_span[0]], line[Name_span[1]:])
			print(newline, end='')
			# print mapping of old names to new names
			print('{0}\t{1}'.format(ID_match.group(1), model), file=sys.stderr)


		elif '\tmRNA\t' in line:
			ID_match = re.search('ID=(.+?)-mRNA-1;', line)

			if ID_match.group(1) != lastmodel:
				sys.exit('''GFF not sorted properly! The input gff is expected to be sorted such that subordinate
features directly follow their parent gene feature and before the next gene feature.

line: {0}
last model: {1}
this model: {2}'''.format(line, lastmodel, ID_match.group(1)))

			ID_span = ID_match.span(1)
			Parent_match = re.search('Parent=(.+?);', line)
			Parent_span = Parent_match.span(1)
			Name_match = re.search('Name=(.+?)-mRNA-1;', line)
			Name_span = Name_match.span(1)
			newline = '{0}{1}{2}{1}{3}{1}{4}'.format(line[:ID_span[0]], model, line[ID_span[1]:Parent_span[0]], line[Parent_span[1]:Name_span[0]], line[Name_span[1]:])
			print(newline, end='')


#		elif '\texon\t' in line:
#			ID_match = re.search('ID=(.+?)-mRNA-1:', line)
#
#			if ID_match.group(1) != lastmodel:
#				sys.exit('''GFF not sorted properly! The input gff is expected to be sorted such that subordinate
#features directly follow their parent gene feature and before the next gene feature.
#
#line: {0}
#last model: {1}
#this model: {2}'''.format(line, lastmodel, ID_match.group(1)))
#
#			ID_span = ID_match.span(1)
#			Parent_match = re.search('Parent=(.+?)$', line)
#			Parent_span = Parent_match.span(1)
#			newline = '{0}{1}{2}{1}{3}'.format(line[:ID_span[0]], model, line[ID_span[1]:Parent_span[0]], line[Parent_span[1]:])
#			print(newline)


		elif '\texon\t' in line or '\tCDS\t' in line or '\tfive_prime_UTR\t' in line or '\tthree_prime_UTR\t' in line:
			ID_match = re.search('ID=(.+?)-mRNA-1:', line)

			if ID_match.group(1) != lastmodel:
				sys.exit('''GFF not sorted properly! The input gff is expected to be sorted such that subordinate
features directly follow their parent gene feature and before the next gene feature.

line: {0}
last model: {1}
this model: {2}'''.format(line, lastmodel, ID_match.group(1)))

			ID_span = ID_match.span(1)
			Parent_match = re.search('Parent=(.+?)$', line)
			Parent_span = Parent_match.span(1)
			newline = '{0}{1}{2}{1}{3}'.format(line[:ID_span[0]], model, line[ID_span[1]:Parent_span[0]], line[Parent_span[1]:])
			print(newline, end='')


#		elif '\tfive_prime_UTR\t' in line:
#			scaf = line.split('\t')[0]
#			genemodel = 'g' + str(modelnum).zfill(6)
#			model = '{0}_{1}.{2}'.format(prefix, scaf, genemodel)
#			ID_match = re.search('ID=(.+);', line)
#			ID_span = ID_match.span(1)
#			Name_match = re.search('Name=(.+)$', line)
#			Name_span = Name_match.span(1)
#			newline = '{0}{1}{2}{1}{3}'.format(line[:ID_span[0]], model, line[ID_span[1]:Name_span[0]], line[Name_span[1]:])
#			print(newline)
#
#
#		elif '\tthree_prime_UTR\t' in line:
#			scaf = line.split('\t')[0]
#			genemodel = 'g' + str(modelnum).zfill(6)
#			model = '{0}_{1}.{2}'.format(prefix, scaf, genemodel)
#			ID_match = re.search('ID=(.+);', line)
#			ID_span = ID_match.span(1)
#			Name_match = re.search('Name=(.+)$', line)
#			Name_span = Name_match.span(1)
#			newline = '{0}{1}{2}{1}{3}'.format(line[:ID_span[0]], model, line[ID_span[1]:Name_span[0]], line[Name_span[1]:])
#			print(newline)

		else:
			print(line, end='')
