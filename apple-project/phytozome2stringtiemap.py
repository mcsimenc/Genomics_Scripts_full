#!/usr/bin/env python3

import sys

# usage:
#	this_script.py < abundances.guided.out

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

overlaps = {}
M = {}
for line in sys.stdin:
	if line.startswith('Gene ID'):
		continue
	
	gene_id, gene_name, scaf, strand, start, end, coverage, fpkm, tpm = line.strip().split()
	if gene_name != '-':
		if scaf in  overlaps:
			assert gene_name not in overlaps[scaf]
			overlaps[scaf][gene_name] = {strand:(start,end)}
		else:
			overlaps[scaf] = {gene_name:{strand:(start,end)}}
	else:
		if scaf not in overlaps:
			continue
		for g in overlaps[scaf]:
			if strand in overlaps[scaf][g]:
				if Overlaps(overlaps[scaf][g][strand], (start,end)):
					M[gene_id] = g
					print('{0}\t{1}'.format(M[gene_id],gene_id))

#for st_g in M:
#	print('{0}\t{1}'.format(M[st_g],st_g))
		
		
		
	

#Gene ID	Gene Name	Reference	Strand	Start	End	Coverage	FPKM	TPM
#MDP0000856242.GDRv1.0	MDP0000856242	MDC000002.223	+	816	1094	47.345879	0.856326	0.908239
#GrannySmithRNAseqStringTie.1	-	MDC000002.223	+	816	1094	47.345879	0.856326	0.908239
#MDP0000350535.GDRv1.0	MDP0000350535	MDC000002.325	+	219	1102	447.734497	8.097994	8.588916
#GrannySmithRNAseqStringTie.2	-	MDC000002.325	+	219	1102	447.734497	8.097994	8.588916
#GrannySmithRNAseqStringTie.3	-	MDC000002.325	.	3710	5739	13.521182	0.487547	0.517104
#MDP0000134856.GDRv1.0	MDP0000134856	MDC000002.325	-	1806	3635	22.769489	0.411823	0.436788
#GrannySmithRNAseqStringTie.4	-	MDC000002.325	-	1805	3587	19.382502	0.350564	0.371816
#GrannySmithRNAseqStringTie.5	-	MDC000002.325	.	6261	7255	112.541710	3.842050	4.074965
#GrannySmithRNAseqStringTie.6	-	MDC000003.55	.	3808	4526	12.802504	0.459317	0.487162
