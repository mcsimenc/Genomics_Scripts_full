#!/usr/bin/env python3

import sys

# Just give a GFF with tRNAscan annotations on stdin and out will come total/single/multi-exon genes for Pseudogenes and putative functional genes


psuedo_multi_exon_ct = 0
functional_multi_exon_ct = 0
psuedo_single_exon_ct = 0
functional_single_exon_ct = 0

exon_ct = None
PSEUDO = None
for line in sys.stdin:
	if 'trnascan' in line:
		if '\tgene\t' in line:


			if not exon_ct == None and not PSEUDO == None:
				if exon_ct == 1:
					if PSEUDO == True:
						psuedo_single_exon_ct += 1
					elif PSEUDO == False:
						functional_single_exon_ct += 1
					else:
						sys.exit('Something happened...PSEUDO and not PSUEDO? line 26')
				elif exon_ct > 1:
					if PSEUDO == True:
						psuedo_multi_exon_ct += 1
					elif PSEUDO == False:
						functional_multi_exon_ct += 1
					else:
						sys.exit('Something happened...PSEUDO and not PSUEDO? line 34')

				else:
					sys.exit('Something happened...exon_ct == {0}'.format(exon_ct))
					
					
			exon_ct = 0

			if 'Pseudo' in line:
				PSEUDO = True
			else:
				PSEUDO = False

		if '\texon\t' in line:
			exon_ct += 1


if exon_ct == 1:
	if PSEUDO == True:
		psuedo_single_exon_ct += 1
	elif PSEUDO == False:
		functional_single_exon_ct += 1
	else:
		sys.exit('Something happened...PSEUDO and not PSUEDO? line 26')
elif exon_ct > 1:
	if PSEUDO == True:
		psuedo_multi_exon_ct += 1
	elif PSEUDO == False:
		functional_multi_exon_ct += 1
	else:
		sys.exit('Something happened...PSEUDO and not PSUEDO? line 34')

else:
	sys.exit('Something happened...exon_ct == {0}'.format(exon_ct))

print('multi-exon_pseudogenes:\t{0}\nsingle-exon_pseudogenes:\t{1}\nmulti-exon_functional_genes:\t{2}\nsingle-exon_functional_genes:\t{3}'.format(psuedo_multi_exon_ct, psuedo_single_exon_ct, functional_multi_exon_ct,  functional_single_exon_ct))
