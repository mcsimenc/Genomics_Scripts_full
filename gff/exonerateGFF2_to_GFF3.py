#!/usr/bin/env python3

import sys

def help():
	print('''
 Usage:
 ------------
 exonerateGFF2_to_GFF3.py < file.gff3 > file.gff3
 
 Description:
 ------------
 Converts GFF2 file from stdin to GFF3 file on stdout.
 Written for Exonerate's GFF2 output, which has extra
 lines.

 Example input
 ------------
 Command line: [exonerate --query Trinity.fasta --target Mdomestica_196_v1.0.fa --model est2genome --showalignment FALSE --showtargetgff TRUE --showvulgar FALSE]
 Hostname: [kepler-0-1.local]
 # --- START OF GFF DUMP ---
 #
 #
 ##gff-version 2
 ##source-version exonerate:est2genome 2.2.0
 ##date 2018-10-20
 ##type DNA
 #
 #
 # seqname source feature start end score strand frame attributes
 #
 MDC000001.113	exonerate:est2genome	gene	164	321	112	-	.	gene_id 1 ; sequence TRINITY_DN57_c2_g1_i2 ; gene_orientation .
 MDC000001.113	exonerate:est2genome	exon	164	321	.	-	.	insertions 8 ; deletions 10
 MDC000001.113	exonerate:est2genome	similarity	164	321	112	-	.	alignment_id 1 ; Query TRINITY_DN57_c2_g1_i2 ; Align 322 210 41 ; Align 281 252 22 ; Align 258 274 6 ; Align 251 280 17 ; Align 234 298 1 ; Align 233 302 4 ; Align 227 306 8 ; Align 219 315 27 ; Align 192 346 7 ; Align 183 353 7 ; Align 174 360 10
 # --- END OF GFF DUMP ---
 #
 # --- START OF GFF DUMP ---
 #
 ''')

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

	def __repr__(self):
		'''
		Defines str() and repr() behavior
		'''
		self.refreshAttrStr()
		return '\t'.join( [ str(self.seqid), str(self.source), str(self.type), str(self.start), str(self.end), str(self.score), str(self.strand), str(self.phase), str(self.attributes_str) ] )

	def addAttr(self, attr_key, attr_val, replace=False, attr_pos=0):
		'''
		Adds attribute, default is at the start of the list.
		Default behavior is to add attr_val to a growing
		comma-sep list if attr_key exists. Set replace=True to
		replace existing attr_val.
		'''
		if attr_key in self.attributes:
			if replace:
				delAttr(attr_key)
				self.attributes[attr_key] = attr_val
				self.attributes_order.insert(attr_pos, attr_key)
				self.refreshAttrStr()
			else: # grow list
				self.attributes[attr_key] = '{0},{1}'.format(self.attributes[attr_key], attr_val)
				self.refreshAttrStr()
		else:
			self.attributes[attr_key] = attr_val
			self.attributes_order.insert(attr_pos, attr_key)
			self.refreshAttrStr()

	def delAttr(self, attr_key):
		'''
		Deletes attribute.
		'''
		del self.attributes[attr_key]
		self.attributes_order.pop(self.attributes_order.index(attr_key))
		self.refreshAttrStr()

	def refreshAttrStr(self, attrOrder=None):
		'''
		If the attributes have been changed this needs to be called
		before the changes are reflected on a str() call on this object.

		If an attribute has been added it should have also been added to self.attributes_order
		'''
		self.attributes_str = ';'.join([ '='.join([ attr, self.attributes[attr] ]) for attr in self.attributes_order ])

def convert_GFF2_to_GFF3(line):
	'''
	Requires class GFF3_line
	Takes a GFF2-format line line and returns a GFF3 obj
	'''
	gff3 = GFF3_line()
	#print(line.strip().split('\t'))
	if len(line.strip().split('\t')) == 9:
		gff3.seqid, gff3.source, gff3.type, gff3.start, gff3.end, gff3.score, gff3.strand, gff3.phase, attr = line.strip().split('\t')
		if gff3.type == 'similarity':
			return None
		attr = attr.split(';')
		for pair in attr:
			k,v = pair.split()
			gff3.attributes[k] = v
			gff3.attributes_order.append(k)
			gff3.refreshAttrStr()
	elif len(line.strip().split('\t')) == 8:
		gff3.seqid, gff3.source, gff3.type, gff3.start, gff3.end, gff3.score, gff3.strand, gff3.phase = line.strip().split('\t')
		gff3.attributes['ID'] = '.'
		gff3.attributes_order.append('ID')
		if gff3.type == 'similarity':
			return None

	return gff3
	
	
def Overlaps(j, k):
	'''
	Inputs, j and k, are tuples/lists with a start and a end coordinate as in: (start, end)
	If they overlap True is returned, if they do not overlap, False is returned.
	'''
	j = sorted([int(i) for i in j])
	k = sorted([int(i) for i in k])
	jk = sorted([j,k], key=lambda x:x[0])
	if jk[0][1] >= jk[1][0]:
		return True
	else:
		return False

# ---------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	args = sys.argv

	if '-h' in args:
		help()
		sys.exit()

	if '-stdout' in args:
		PRINT = True
	else:
		PRINT = False

	BEGIN = False
	print('##gff-version 3')
	feats = {}
	for line in sys.stdin:
		if line.startswith('#'):
			BEGIN = True
			continue
		elif BEGIN:
			gff3 = convert_GFF2_to_GFF3(line)
			if not gff3 == None:
				if PRINT:
					print(str(gff3))
				scaf = gff3.seqid
				coords = (gff3.start,gff3.end)
				# Combine feats with identical type and coords, adding evidence (transcript) to master record
				if scaf in feats:
					if coords in feats[scaf]:
						if gff3.type in feats[scaf][coords]:
							if 'sequence' in gff3.attributes:
								feats[scaf][coords][gff3.type].addAttr(attr_key='sequence', attr_val=gff3.attributes['sequence'])
						else:
							feats[scaf][coords][gff3.type] = gff3
					else:
						feats[scaf][coords] = { gff3.type:gff3 }
				else:
					feats[scaf] = {coords:{gff3.type:gff3}}
	# print GFF3 lines
	for scaf in feats:
		for t in feats[scaf]:
			for c in feats[scaf][t]:
				print(str(feats[scaf][t][c]))
