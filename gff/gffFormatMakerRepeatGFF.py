#!/usr/bin/env python3

import sys
import re


def help():
	print('''
			usage:
				gffAddAttr.py -gff <filepath> -attr <string> -map <filepath> -mapKey <string> > output.gff


			description: Adds a new attribute to field 9 of input gff. 

			-attr	<string>	New attribute name. Throws an error if the name is taken.

			-gff	<filepath>	Input GFF3 file

			-map	<filepath>	Two column tab delimited file where first field corresponds
						to the value of the attribute specified by -mapKey and the second
						to the value for the new attribute.

			-mapKey	<string>	The attribute for which the first field of the -map file is derived.

			-restrictType <string>	Only add new attribute to features of this type

			-replace		Replace existing attribute if present

			-replaceIfNone		Replace existing attribute if present and is 'None'

			-v			Verbose reporting on stderr

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

if '-h' in args:
	help()

simpleRepeatPattern = re.compile('%\d+([ACTG]+)%')

for line in sys.stdin:
	if line.startswith('#'):
		print(line, end='')
		continue

	gffLine = GFF3_line(line)

	nameAttr = gffLine.attributes['Name']
	targetAttr = gffLine.attributes['Target']

	nameAttr = nameAttr.split('species:')[-1].split('|genus:')
	targetAttr = targetAttr.split('species:')[-1].split(' ')
	if nameAttr[-1] in nameAttr[0] or nameAttr[-1] == 'Unspecified':
		nameAttr = nameAttr[0]
		targetAttr = '{0}_{1}'.format(nameAttr, '_'.join(targetAttr[-3:]))
	elif nameAttr[-1] == 'Simple_repeat':
		rpt = re.search(simpleRepeatPattern, nameAttr[0]).group(1)
		nameAttr = '{0}_({1})n'.format(nameAttr[-1], rpt)
		targetAttr = '{0}_{1}'.format(nameAttr, '_'.join(targetAttr[-3:]))
	elif nameAttr[-1] == 'Satellite' and '%' in nameAttr[0]:
		rpt = re.search(simpleRepeatPattern, nameAttr[0]).group(1)
		nameAttr = '{0}_({1})n'.format(nameAttr[-1], rpt)
		targetAttr = '{0}_{1}'.format(nameAttr, '_'.join(targetAttr[-3:]))
	elif '%252F' in nameAttr[-1]:
		firstPart = nameAttr[-1].split('%252F')
		if nameAttr[0].startswith(firstPart[-1]):
			firstPart = firstPart[0]
		else:
			firstPart = '_'.join(firstPart)
		nameAttr = '{0}_{1}'.format(firstPart, nameAttr[0])
		targetAttr = '{0}_{1}'.format(nameAttr, '_'.join(targetAttr[-3:]))
	elif '%2F' in nameAttr[-1]:
		firstPart = nameAttr[-1].split('%2F')
		if nameAttr[0].startswith(firstPart[-1]):
			firstPart = firstPart[0]
		else:
			firstPart = '_'.join(firstPart)
		nameAttr = '{0}_{1}'.format(firstPart, nameAttr[0])
		targetAttr = '{0}_{1}'.format(nameAttr, '_'.join(targetAttr[-3:]))
	else:
		nameAttr = '{0}_{1}'.format(nameAttr[-1], nameAttr[0])
		targetAttr = '{0}_{1}'.format(nameAttr, '_'.join(targetAttr[-3:]))
	
	gffLine.attributes['Name'] = targetAttr
	#gffLine.attributes['Target'] = targetAttr
	del(gffLine.attributes['Target'])
	gffLine.attributes_order.pop(gffLine.attributes_order.index('Target'))
	gffLine.refreshAttrStr()
	print(str(gffLine))


	



#ID=Azfi_s0001:hit:139:1.3.0.0
#Name=species:%28TA%29n|genus:Simple_repeat
#Target=species:%28TA%29n|genus:Simple_repeat 1 22 +
#;Dfam_2.0_annotation=None
#Repbase_22.04_annotation=None
#
#ID=Azfi_s0001:hit:191:1.3.0.0;
#Name=species:deg7180000005503|quiver|genus:Unspecified
#Target=species:deg7180000005503|quiver|genus:Unspecified 1014 1371 +
#Dfam_2.0_annotation=None
#Repbase_22.04_annotation=None
#
#ID=Azfi_s0001:hit:192:1.3.0.0
#Name=species:SSU-rRNA_Ath|genus:rRNA
#Target=species:SSU-rRNA_Ath|genus:rRNA 86 1891 +
#Dfam_2.0_annotation=SSU-rRNA_Hsa
#Repbase_22.04_annotation=SSU-rRNA_Ath
#
#ID=Azfi_s0001:hit:193:1.3.0.0
#Name=species:RM_24141_rnd-3_family-26|genus:Unspecified
#Target=species:RM_24141_rnd-3_family-26|genus:Unspecified 1723 2418 +
#Dfam_2.0_annotation=None
#Repbase_22.04_annotation=SSU-rRNA_Lvi
#
#ID=Azfi_s0001:hit:45:1.3.0.0
#Name=species:GA-rich|genus:Low_complexity
#Target=species:GA-rich|genus:Low_complexity 1 57 +
#Dfam_2.0_annotation=None
#Repbase_22.04_annotation=None
