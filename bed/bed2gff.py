#!/usr/bin/env python3

# converts from BED format as in bedops gff2bed output to GFF3 format
import sys


for line in sys.stdin:

	if line.startswith('#'):
		print(line)

	else:
		(scaf, bed_start, bed_end, name, score, strand, source, Type, unknown, attr)  = line.strip().split('\t')

		gff_start = str(int(bed_start) + 1)
		gff_end = bed_end

		print('\t'.join([scaf, source, Type, gff_start, gff_end, score, strand, '.', attr]))


# BED
# Scaf, start, end, Name, score, strand, source, type, attr

#Azfi_s0001	0	565	Azfi_s0001:hit:191:1.3.0.0	2.94e+03	+	repeatmasker	match	.	ID=Azfi_s0001:hit:191:1.3.0.0;Name=species:deg7180000005503|quiver|genus:Unspecified;Target=species:deg7180000005503|quiver|genus:Unspecified 1014 1371 +

# GFF
# Scaf, source, type, start, end, score, strand, phase, attr

#Azfi_s4737	repeatmasker	match	6334	6375	12	+	.	ID=Azfi_s4737:hit:173539:1.3.0.0;Name=species:A-rich|genus:Low_complexity;Target=species:A-rich|genus:Low_complexity 1 44 +
