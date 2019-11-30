#!/usr/bin/env python3

import sys

def help():
	print('''
 Usage:
 ------------
 makergff2evidence.py < <gff>
 
 Description:
 ------------
 Summarizes evidence (ONLY EXONERATE est2genome) from MAKER GFF3
 for genes

 ''')

class GFF3_line:
	'''
	Attributes:
			field0, ... , field8 - string
			attributes - dictionary

	Methods:    str()		
				prints gff line
		    refreshAttrStr()
				updates gff line attributes
		    addAttr(key, val, replace=False, attr_pos=0)
				adds attr
		    delAttr(key)
				removes attr
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

	def refreshAttrStr(self, attrOrder=None):
		'''
		If the attributes have been changed this needs to be called
		before the changes are reflected on a str() call on this object.

		If an attribute has been added it should have also been added to self.attributes_order
		'''
		self.attributes_str = ';'.join([ '='.join([ attr, self.attributes[attr] ]) for attr in self.attributes_order ])

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

if __name__ == '__main__':
	args = sys.argv
	if '-h' in args:
		help()
		sys.exit()
	Map = {}
	gene, scaf, coords = [None]*3
	for line in sys.stdin:
		if line.startswith('#'):
			continue
		if line.startswith('>'):
			break
		gff3Line = GFF3_line(line)
		if gff3Line.source == 'maker':
			if gff3Line.type == 'gene':
				gene = gff3Line.attributes['ID']
				scaf = gff3Line.seqid
				coords = (gff3Line.start, gff3Line.end)
				Map[gene] = set()
		elif gff3Line.source == 'est2genome':
			if gff3Line.type == 'expressed_sequence_match':
				if gene == None:
					continue
				if gff3Line.seqid == scaf:
					c2 = (gff3Line.start, gff3Line.end)
					if Overlaps(c2, coords):
						expr = gff3Line.attributes['Name']
						Map[gene].add(expr)
	for g in Map:
		for e in Map[g]:
			print('{0}\t{1}'.format(e, g))

#MDC006612.174	maker	gene	3327	4144	.	-	.	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0;Name=maker-MDC006612.174-exonerate_est2genome-gene-0.0
#MDC006612.174	maker	mRNA	3327	4144	1379	-	.	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0;Name=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1;_AED=0.27;_eAED=0.27;_QI=43|1|1|1|0|0|3|0|80
#MDC006612.174	maker	exon	3327	3440	.	-	.	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1:exon:482;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1
#MDC006612.174	maker	exon	3840	3897	.	-	.	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1:exon:481;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1
#MDC006612.174	maker	exon	4034	4144	.	-	.	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1:exon:480;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1
#MDC006612.174	maker	five_prime_UTR	4102	4144	.	-	.	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1:five_prime_utr;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1
#MDC006612.174	maker	CDS	4034	4101	.	-	0	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1:cds;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1
#MDC006612.174	maker	CDS	3840	3897	.	-	1	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1:cds;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1
#MDC006612.174	maker	CDS	3327	3440	.	-	0	ID=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1:cds;Parent=maker-MDC006612.174-exonerate_est2genome-gene-0.0-mRNA-1
####
#MDC006612.174	repeatmasker	match	2590	2632	15	+	.	ID=MDC006612.174:hit:5378:1.3.0.0;Name=species:%28CTACTCT%29n|genus:Simple_repeat;Target=species:%28CTACTCT%29n|genus:Simple_repeat 1 44 +
#MDC006612.174	repeatmasker	match_part	2590	2632	15	+	.	ID=MDC006612.174:hsp:8861:1.3.0.0;Parent=MDC006612.174:hit:5378:1.3.0.0;Target=species:%2528CTACTCT%2529n|genus:Simple_repeat 1 44 +
#MDC006612.174	repeatmasker	match	3619	3640	20	+	.	ID=MDC006612.174:hit:5379:1.3.0.0;Name=species:%28AG%29n|genus:Simple_repeat;Target=species:%28AG%29n|genus:Simple_repeat 1 22 +
#MDC006612.174	repeatmasker	match_part	3619	3640	20	+	.	ID=MDC006612.174:hsp:8862:1.3.0.0;Parent=MDC006612.174:hit:5379:1.3.0.0;Target=species:%2528AG%2529n|genus:Simple_repeat 1 22 +
#MDC006612.174	repeatmasker	match	2590	2632	15	+	.	ID=MDC006612.174:hit:5380:1.3.0.0;Name=species:%28CTACTCT%29n|genus:Simple_repeat;Target=species:%28CTACTCT%29n|genus:Simple_repeat 1 44 +
#MDC006612.174	repeatmasker	match_part	2590	2632	15	+	.	ID=MDC006612.174:hsp:8863:1.3.0.0;Parent=MDC006612.174:hit:5380:1.3.0.0;Target=species:%2528CTACTCT%2529n|genus:Simple_repeat 1 44 +
#MDC006612.174	repeatmasker	match	3619	3640	20	+	.	ID=MDC006612.174:hit:5381:1.3.0.0;Name=species:%28AG%29n|genus:Simple_repeat;Target=species:%28AG%29n|genus:Simple_repeat 1 22 +
#MDC006612.174	repeatmasker	match_part	3619	3640	20	+	.	ID=MDC006612.174:hsp:8864:1.3.0.0;Parent=MDC006612.174:hit:5381:1.3.0.0;Target=species:%2528AG%2529n|genus:Simple_repeat 1 22 +
#MDC006612.174	repeatmasker	match	2	1050	4944	+	.	ID=MDC006612.174:hit:5382:1.3.0.0;Name=species:Gypsy-32_Mad-I|genus:LTR%2FGypsy;Target=species:Gypsy-32_Mad-I|genus:LTR%2FGypsy 2433 3142 +
#MDC006612.174	repeatmasker	match_part	2	1050	4944	+	.	ID=MDC006612.174:hsp:8865:1.3.0.0;Parent=MDC006612.174:hit:5382:1.3.0.0;Target=species:Gypsy-32_Mad-I|genus:LTR%252FGypsy 2433 3142 +
#MDC006612.174	repeatmasker	match	1719	2190	535	+	.	ID=MDC006612.174:hit:5383:1.3.0.0;Name=species:DNA3-7_Mad|genus:DNA;Target=species:DNA3-7_Mad|genus:DNA 596 1144 +
#MDC006612.174	repeatmasker	match_part	1719	2190	535	+	.	ID=MDC006612.174:hsp:8866:1.3.0.0;Parent=MDC006612.174:hit:5383:1.3.0.0;Target=species:DNA3-7_Mad|genus:DNA 596 1144 +
#MDC006612.174	repeatmasker	match	3942	4037	277	+	.	ID=MDC006612.174:hit:5384:1.3.0.0;Name=species:Zisupton-6_DR|genus:DNA%2FZisupton;Target=species:Zisupton-6_DR|genus:DNA%2FZisupton 8640 8732 +
#MDC006612.174	repeatmasker	match_part	3942	4037	277	+	.	ID=MDC006612.174:hsp:8867:1.3.0.0;Parent=MDC006612.174:hit:5384:1.3.0.0;Target=species:Zisupton-6_DR|genus:DNA%252FZisupton 8640 8732 +
####
#MDC006612.174	blastn	expressed_sequence_match	1240	1545	114	-	.	ID=MDC006612.174:hit:5385:3.2.0.0;Name=TRINITY_DN20924_c0_g1_i1
#MDC006612.174	blastn	match_part	1240	1545	114	-	.	ID=MDC006612.174:hsp:8868:3.2.0.0;Parent=MDC006612.174:hit:5385:3.2.0.0;Target=TRINITY_DN20924_c0_g1_i1 87 393 +;Gap=M121 I2 M28 D1 M156
#MDC006612.174	blastn	expressed_sequence_match	1244	1545	122	-	.	ID=MDC006612.174:hit:5386:3.2.0.0;Name=TRINITY_DN20924_c0_g1_i3
#MDC006612.174	blastn	match_part	1244	1545	122	-	.	ID=MDC006612.174:hsp:8869:3.2.0.0;Parent=MDC006612.174:hit:5386:3.2.0.0;Target=TRINITY_DN20924_c0_g1_i3 87 389 +;Gap=M121 I2 M28 D1 M152
#MDC006612.174	blastn	expressed_sequence_match	1114	1296	96	+	.	ID=MDC006612.174:hit:5387:3.2.0.0;Name=TRINITY_DN63003_c0_g1_i1
#MDC006612.174	blastn	match_part	1114	1296	96	+	.	ID=MDC006612.174:hsp:8870:3.2.0.0;Parent=MDC006612.174:hit:5387:3.2.0.0;Target=TRINITY_DN63003_c0_g1_i1 203 388 +;Gap=M41 I3 M142
#MDC006612.174	blastn	expressed_sequence_match	3576	3860	210	-	.	ID=MDC006612.174:hit:5388:3.2.0.0;Name=TRINITY_DN77411_c0_g1_i1
#MDC006612.174	blastn	match_part	3576	3860	210	-	.	ID=MDC006612.174:hsp:8871:3.2.0.0;Parent=MDC006612.174:hit:5388:3.2.0.0;Target=TRINITY_DN77411_c0_g1_i1 47 333 +;Gap=M220 I2 M65
#MDC006612.174	blastn	expressed_sequence_match	4619	4824	206	+	.	ID=MDC006612.174:hit:5389:3.2.0.0;Name=TRINITY_DN5501_c22352_g1_i1
#MDC006612.174	blastn	match_part	4619	4824	206	+	.	ID=MDC006612.174:hsp:8872:3.2.0.0;Parent=MDC006612.174:hit:5389:3.2.0.0;Target=TRINITY_DN5501_c22352_g1_i1 1 206 +;Gap=M206
#MDC006612.174	blastn	expressed_sequence_match	3327	4144	57	-	.	ID=MDC006612.174:hit:5390:3.2.0.0;Name=TRINITY_DN24934_c0_g1_i1
#MDC006612.174	blastn	match_part	4088	4144	57	-	.	ID=MDC006612.174:hsp:8873:3.2.0.0;Parent=MDC006612.174:hit:5390:3.2.0.0;Target=TRINITY_DN24934_c0_g1_i1 1 57 +;Gap=M57
#MDC006612.174	blastn	match_part	3839	3891	53	-	.	ID=MDC006612.174:hsp:8874:3.2.0.0;Parent=MDC006612.174:hit:5390:3.2.0.0;Target=TRINITY_DN24934_c0_g1_i1 118 170 +;Gap=M53
#MDC006612.174	blastn	match_part	3327	3440	114	-	.	ID=MDC006612.174:hsp:8875:3.2.0.0;Parent=MDC006612.174:hit:5390:3.2.0.0;Target=TRINITY_DN24934_c0_g1_i1 170 283 +;Gap=M114
#MDC006612.174	blastn	expressed_sequence_match	3193	5179	104	+	.	ID=MDC006612.174:hit:5391:3.2.0.0;Name=TRINITY_DN12871_c0_g1_i2
#MDC006612.174	blastn	match_part	3193	3440	104	+	.	ID=MDC006612.174:hsp:8876:3.2.0.0;Parent=MDC006612.174:hit:5391:3.2.0.0;Target=TRINITY_DN12871_c0_g1_i2 290 537 +;Gap=M248
#MDC006612.174	blastn	match_part	4088	5179	918	+	.	ID=MDC006612.174:hsp:8877:3.2.0.0;Parent=MDC006612.174:hit:5391:3.2.0.0;Target=TRINITY_DN12871_c0_g1_i2 647 1738 +;Gap=M1092
#MDC006612.174	blastn	expressed_sequence_match	3005	3440	412	+	.	ID=MDC006612.174:hit:5392:3.2.0.0;Name=TRINITY_DN19363_c0_g1_i1
#MDC006612.174	blastn	match_part	3005	3440	412	+	.	ID=MDC006612.174:hsp:8878:3.2.0.0;Parent=MDC006612.174:hit:5392:3.2.0.0;Target=TRINITY_DN19363_c0_g1_i1 1 436 +;Gap=M436
#MDC006612.174	blastn	expressed_sequence_match	3433	3677	195	+	.	ID=MDC006612.174:hit:5393:3.2.0.0;Name=TRINITY_DN64338_c0_g1_i1
#MDC006612.174	blastn	match_part	3433	3677	195	+	.	ID=MDC006612.174:hsp:8879:3.2.0.0;Parent=MDC006612.174:hit:5393:3.2.0.0;Target=TRINITY_DN64338_c0_g1_i1 1 248 +;Gap=M69 I3 M176
#MDC006612.174	blastn	expressed_sequence_match	2651	3151	501	-	.	ID=MDC006612.174:hit:5394:3.2.0.0;Name=TRINITY_DN57176_c0_g1_i1
#MDC006612.174	blastn	match_part	2651	3151	501	-	.	ID=MDC006612.174:hsp:8880:3.2.0.0;Parent=MDC006612.174:hit:5394:3.2.0.0;Target=TRINITY_DN57176_c0_g1_i1 4 504 +;Gap=M501
#MDC006612.174	blastn	expressed_sequence_match	2651	2867	217	-	.	ID=MDC006612.174:hit:5395:3.2.0.0;Name=TRINITY_DN57176_c0_g1_i2
#MDC006612.174	blastn	match_part	2651	2867	217	-	.	ID=MDC006612.174:hsp:8881:3.2.0.0;Parent=MDC006612.174:hit:5395:3.2.0.0;Target=TRINITY_DN57176_c0_g1_i2 64 280 +;Gap=M217
#MDC006612.174	est2genome	expressed_sequence_match	1205	1641	1540	-	.	ID=MDC006612.174:hit:5396:3.2.0.0;Name=TRINITY_DN20924_c0_g1_i1
#MDC006612.174	est2genome	match_part	1205	1641	1540	-	.	ID=MDC006612.174:hsp:8882:3.2.0.0;Parent=MDC006612.174:hit:5396:3.2.0.0;Target=TRINITY_DN20924_c0_g1_i1 1 437 +;Gap=M28 I1 M13 D6 M2 D1 M2 D4 M161 I2 M28 D1 M150 I9 M41
#MDC006612.174	est2genome	expressed_sequence_match	1130	1641	1519	-	.	ID=MDC006612.174:hit:5397:3.2.0.0;Name=TRINITY_DN20924_c0_g1_i3
#MDC006612.174	est2genome	match_part	1130	1641	1519	-	.	ID=MDC006612.174:hsp:8883:3.2.0.0;Parent=MDC006612.174:hit:5397:3.2.0.0;Target=TRINITY_DN20924_c0_g1_i3 1 494 +;Gap=M28 I1 M13 D6 M2 D1 M2 D4 M161 I2 M28 D1 M169 D1 M38 D1 M13 D3 M13 D4 M24
#MDC006612.174	est2genome	expressed_sequence_match	898	1296	1555	-	.	ID=MDC006612.174:hit:5398:3.2.0.0;Name=TRINITY_DN63003_c0_g1_i1
#MDC006612.174	est2genome	match_part	898	1296	1555	-	.	ID=MDC006612.174:hsp:8884:3.2.0.0;Parent=MDC006612.174:hit:5398:3.2.0.0;Target=TRINITY_DN63003_c0_g1_i1 1 388 -;Gap=M42 D10 M4 D3 M23 D2 M50 I1 M22 I2 M57 D2 M42 I3 M142
#MDC006612.174	est2genome	expressed_sequence_match	3576	3889	1410	+	.	ID=MDC006612.174:hit:5399:3.2.0.0;Name=TRINITY_DN77411_c0_g1_i1
#MDC006612.174	est2genome	match_part	3576	3889	1410	+	.	ID=MDC006612.174:hsp:8885:3.2.0.0;Parent=MDC006612.174:hit:5399:3.2.0.0;Target=TRINITY_DN77411_c0_g1_i1 18 333 -;Gap=M249 I2 M65
#MDC006612.174	est2genome	expressed_sequence_match	4619	4824	1030	-	.	ID=MDC006612.174:hit:5400:3.2.0.0;Name=TRINITY_DN5501_c22352_g1_i1
#MDC006612.174	est2genome	match_part	4619	4824	1030	-	.	ID=MDC006612.174:hsp:8886:3.2.0.0;Parent=MDC006612.174:hit:5400:3.2.0.0;Target=TRINITY_DN5501_c22352_g1_i1 1 206 -;Gap=M206
#MDC006612.174	est2genome	expressed_sequence_match	3327	4144	1379	-	.	ID=MDC006612.174:hit:5401:3.2.0.0;Name=TRINITY_DN24934_c0_g1_i1
#MDC006612.174	est2genome	match_part	4034	4144	1379	-	.	ID=MDC006612.174:hsp:8887:3.2.0.0;Parent=MDC006612.174:hit:5401:3.2.0.0;Target=TRINITY_DN24934_c0_g1_i1 1 111 +;Gap=M111
#MDC006612.174	est2genome	match_part	3840	3897	1379	-	.	ID=MDC006612.174:hsp:8888:3.2.0.0;Parent=MDC006612.174:hit:5401:3.2.0.0;Target=TRINITY_DN24934_c0_g1_i1 112 169 +;Gap=M58
#MDC006612.174	est2genome	match_part	3327	3440	1379	-	.	ID=MDC006612.174:hsp:8889:3.2.0.0;Parent=MDC006612.174:hit:5401:3.2.0.0;Target=TRINITY_DN24934_c0_g1_i1 170 283 +;Gap=M114
#MDC006612.174	est2genome	expressed_sequence_match	2892	5179	7604	+	.	ID=MDC006612.174:hit:5402:3.2.0.0;Name=TRINITY_DN12871_c0_g1_i2
#MDC006612.174	est2genome	match_part	2892	3119	7604	+	.	ID=MDC006612.174:hsp:8890:3.2.0.0;Parent=MDC006612.174:hit:5402:3.2.0.0;Target=TRINITY_DN12871_c0_g1_i2 1 231 +;Gap=M32 I3 M196
#MDC006612.174	est2genome	match_part	3144	3440	7604	+	.	ID=MDC006612.174:hsp:8891:3.2.0.0;Parent=MDC006612.174:hit:5402:3.2.0.0;Target=TRINITY_DN12871_c0_g1_i2 232 537 +;Gap=M21 I9 M276
#MDC006612.174	est2genome	match_part	3840	3897	7604	+	.	ID=MDC006612.174:hsp:8892:3.2.0.0;Parent=MDC006612.174:hit:5402:3.2.0.0;Target=TRINITY_DN12871_c0_g1_i2 538 592 +;Gap=M46 D3 M9
#MDC006612.174	est2genome	match_part	4034	5179	7604	+	.	ID=MDC006612.174:hsp:8893:3.2.0.0;Parent=MDC006612.174:hit:5402:3.2.0.0;Target=TRINITY_DN12871_c0_g1_i2 593 1738 +;Gap=M1146
#MDC006612.174	est2genome	expressed_sequence_match	3005	3451	2146	-	.	ID=MDC006612.174:hit:5403:3.2.0.0;Name=TRINITY_DN19363_c0_g1_i1
#MDC006612.174	est2genome	match_part	3005	3451	2146	-	.	ID=MDC006612.174:hsp:8894:3.2.0.0;Parent=MDC006612.174:hit:5403:3.2.0.0;Target=TRINITY_DN19363_c0_g1_i1 1 442 -;Gap=M436 D5 M6
#MDC006612.174	est2genome	expressed_sequence_match	3433	3677	1160	-	.	ID=MDC006612.174:hit:5404:3.2.0.0;Name=TRINITY_DN64338_c0_g1_i1
#MDC006612.174	est2genome	match_part	3433	3677	1160	-	.	ID=MDC006612.174:hsp:8895:3.2.0.0;Parent=MDC006612.174:hit:5404:3.2.0.0;Target=TRINITY_DN64338_c0_g1_i1 1 248 -;Gap=M69 I3 M176
#MDC006612.174	est2genome	expressed_sequence_match	2651	3151	2505	+	.	ID=MDC006612.174:hit:5405:3.2.0.0;Name=TRINITY_DN57176_c0_g1_i1
#MDC006612.174	est2genome	match_part	2651	3151	2505	+	.	ID=MDC006612.174:hsp:8896:3.2.0.0;Parent=MDC006612.174:hit:5405:3.2.0.0;Target=TRINITY_DN57176_c0_g1_i1 4 504 -;Gap=M501
#MDC006612.174	est2genome	expressed_sequence_match	2651	2913	1101	+	.	ID=MDC006612.174:hit:5406:3.2.0.0;Name=TRINITY_DN57176_c0_g1_i2
#MDC006612.174	est2genome	match_part	2651	2913	1101	+	.	ID=MDC006612.174:hsp:8897:3.2.0.0;Parent=MDC006612.174:hit:5406:3.2.0.0;Target=TRINITY_DN57176_c0_g1_i2 21 280 -;Gap=M7 D1 M16 I3 M8 D1 M5 D3 M1 D1 M220
#MDC009457.313	.	contig	1	11386	.	.	.	ID=MDC009457.313;Name=MDC009457.313
####
#MDC009457.313	repeatmasker	match	5366	5396	17	+	.	ID=MDC009457.313:hit:94924:1.3.0.0;Name=species:%28A%29n|genus:Simple_repeat;Target=species:%28A%29n|genus:Simple_repeat 1 31 +
#MDC009457.313	repeatmasker	match_part	5366	5396	17	+	.	ID=MDC009457.313:hsp:157959:1.3.0.0;Parent=MDC009457.313:hit:94924:1.3.0.0;Target=species:%2528A%2529n|genus:Simple_repeat 1 31 +
#MDC009457.313	repeatmasker	match	8267	8292	17	+	.	ID=MDC009457.313:hit:94925:1.3.0.0;Name=species:%28AG%29n|genus:Simple_repeat;Target=species:%28AG%29n|genus:Simple_repeat 1 27 +
#MDC009457.313	repeatmasker	match_part	8267	8292	17	+	.	ID=MDC009457.313:hsp:157960:1.3.0.0;Parent=MDC009457.313:hit:94925:1.3.0.0;Target=species:%2528AG%2529n|genus:Simple_repeat 1 27 +
