#!/usr/bin/env python3

import sys

for line in sys.stdin:
	if not line.startswith('bp_overlap'):
		contents = line.strip().split('\t')
		l1 = int(contents[2])
		l2 = int(contents[5])
		if l1 < l2:
			print(contents[1])
		else:
			print(contents[4])
		

	#bp_overlap	feat1	feat1Len	feat1propOverlap	feat2	feat2Len	feat2propOverlap
	#309	28s_rRNA_0082	6407	0.048	18s_rRNA_0092	1808	0.171
	#72	repeat_region6419	21930	0.003	trnascan-Azfi_s0047-noncoding-Thr_TGT-gene-21.7	72	1.000
	#309	28s_rRNA_0220	6407	0.048	18s_rRNA_0278	1811	0.171
	#34	28s_rRNA_0027	4203	0.008	18s_rRNA_0024	1605	0.021
	#8	repeat_region17767	5394	0.001	repeat_region17766	3291	0.002
	#309	28s_rRNA_0078	6404	0.048	18s_rRNA_0088	1810	0.171
	#571	28s_rRNA_0030	6416	0.089	18s_rRNA_0029	2422	0.236
	#1	repeat_region7148	5535	0.000	repeat_region7149	2017	0.000
	#61	repeat_region1438	7801	0.008	trnascan-Azfi_s0004-noncoding-Pseudo_TCT-gene-4.13	73	0.836
