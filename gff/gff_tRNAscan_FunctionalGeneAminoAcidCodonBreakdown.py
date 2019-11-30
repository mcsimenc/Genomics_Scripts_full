#!/usr/bin/env python3

# Options:
# -scaf		print codons for each scaf
# -combine	use with -scaf. combines all trnas for a given aa

import sys

breakdown = {}
if '-scaf' in sys.argv:
	for line in sys.stdin:

		if 'trnascan' in line:
			if '\ttRNA\t' in line:
				if not 'Pseudo' in line:
					scaf = line.strip().split('\t')[0]
					aa_codon = line.strip().split('\t')[8].split(';')[0].split('noncoding-')[1].split('-gene-')[0].split('_')
					aa = aa_codon[0]
					codon = aa_codon[1]
					if scaf in breakdown:
						if aa in breakdown[scaf]:
							if codon in breakdown[scaf][aa]:
								breakdown[scaf][aa][codon] += 1
							else:
								breakdown[scaf][aa][codon] = 1

						else:
							breakdown[scaf][aa] = {codon:1}
					else:
						breakdown[scaf] = {aa:{codon:1}}

	if '-combine' in sys.argv:
		for scaf in sorted(list(breakdown.keys())):
			for aa in sorted(list(breakdown[scaf].keys())):
				total_aa = 0
				for codon in breakdown[scaf][aa]:
					total_aa += breakdown[scaf][aa][codon]
				print('{0}\t{1}\t{2}'.format(scaf, aa, total_aa))

	else:
		for scaf in sorted(list(breakdown.keys())):
			for aa in sorted(list(breakdown[scaf].keys())):
				for codon in breakdown[scaf][aa]:
					print('{0}\t{1}\t{2}\t{3}'.format(scaf, aa, codon, breakdown[scaf][aa][codon]))

else:
		
	for line in sys.stdin:
		if 'trnascan' in line:
			if '\ttRNA\t' in line:
				if not 'Pseudo' in line:
					aa_codon = line.strip().split('\t')[8].split(';')[0].split('noncoding-')[1].split('-gene-')[0].split('_')
					aa = aa_codon[0]
					codon = aa_codon[1]
					if aa in breakdown:
						if codon in breakdown[aa]:
							breakdown[aa][codon] += 1
						else:
							breakdown[aa][codon] = 1

					else:
						breakdown[aa] = {codon:1}

	if '-combine' in sys.argv:
		combinedByAA = {}

		for aa in sorted(list(breakdown.keys())):
			for codon in breakdown[aa]:
				if aa in combinedByAA:
					combinedByAA[aa] += breakdown[aa][codon]
				else:
					combinedByAA[aa] = breakdown[aa][codon]
			print('{0}\t{1}'.format(aa, combinedByAA[aa]))

		
	else:
		for aa in sorted(list(breakdown.keys())):
			for codon in breakdown[aa]:
				print('{0}\t{1}\t{2}'.format(aa, codon, breakdown[aa][codon]))
				

#Sacu_v1.1_s0001	maker	tRNA	131767	131839	.	+	.	ID=trnascan-Sacu_v1.1_s0001-noncoding-Arg_CCT-gene-1.0-tRNA-1;Parent=trnascan-Sacu_v1.1_s0001-noncoding-Arg_CCT-gene-1.0;Name=trnascan-Sacu_v1.1_s0001-noncoding-Arg_CCT-gene-1.0-tRNA-1;_AED=1.00;_eAED=1.00;_QI=0|-1|0|0|-1|0|1|74|0
#Sacu_v1.1_s0001	maker	tRNA	626195	626268	.	+	.	ID=trnascan-Sacu_v1.1_s0001-noncoding-His_GTG-gene-6.0-tRNA-1;Parent=trnascan-Sacu_v1.1_s0001-noncoding-His_GTG-gene-6.0;Name=trnascan-Sacu_v1.1_s0001-noncoding-His_GTG-gene-6.0-tRNA-1;_AED=1.00;_eAED=1.00;_QI=0|-1|0|0|-1|0|1|75|0
#Sacu_v1.1_s0001	maker	tRNA	657798	657872	.	+	.	ID=trnascan-Sacu_v1.1_s0001-noncoding-Pseudo_TTC-gene-6.3-tRNA-1;Parent=trnascan-Sacu_v1.1_s0001-noncoding-Pseudo_TTC-gene-6.3;Name=trnascan-Sacu_v1.1_s0001-noncoding-Pseudo_TTC-gene-6.3-tRNA-1;_AED=1.00;_eAED=1.00;_QI=0|-1|0|0|-1|0|1|76|0
