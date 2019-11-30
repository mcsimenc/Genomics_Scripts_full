#!/usr/bin/env python3

import sys

last = None
for line in sys.stdin:
	if not line.startswith('#'):
		contents = line.strip().split()
		query_direction = int(contents[6]) - int(contents[7])
		subj_direction = int(contents[8]) - int(contents[9])
		if (query_direction < 1 and subj_direction < 1) or (query_direction > 1 and subj_direction > 1):
			direc = '+'
		else:
			direc = '-'

		
		if contents[0] != last:
			print('{0}\t{1}\t{2}'.format(contents[0], contents[1], direc))
			last = contents[0]



## TBLASTX 2.2.31+
## Query: LTR_retrotransposon1
## Database: /home/derstudent/data/other/RepBase/RepBase22.04/all.blastdb
## Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
## 100 hits found
#LTR_retrotransposon1	SSU-rRNA_Lvi	80.50	318	62	0	638	1591	1700	747	0.0	563
#LTR_retrotransposon1	SSU-rRNA_Lvi	81.01	316	60	0	1590	643	748	1695	0.0	553
#LTR_retrotransposon1	SSU-rRNA_Lvi	80.19	313	62	0	652	1590	1686	748	0.0	550
#LTR_retrotransposon1	SSU-rRNA_Lvi	81.59	315	58	0	1594	650	744	1688	0.0	541
#LTR_retrotransposon1	SSU-rRNA_Lvi	80.00	260	52	0	1589	810	749	1528	0.0	453
