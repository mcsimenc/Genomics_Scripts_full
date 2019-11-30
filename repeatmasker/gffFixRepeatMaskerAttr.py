#!/usr/bin/env python3

import sys



def help():
	print('''
		Usage:
		------------
		gffFixRepeatMaskerAttr.py < input.gff > output.gff

		Description:
		------------
		Formats default GFF3 output from RepeatMasker to have GFF3 style
		attribute column. Example:

		Azfi_s4733	RepeatMasker	similarity	4681	4744	24.1	+	.	Target "Motif:(CGCCGA)n" 1 62
		Azfi_s4737	RepeatMasker	similarity	5482	5530	13.0	-	.	Target "Motif:Gypsy-64_PAb-I" 827 875

		Becomes:

		Azfi_s4733	RepeatMasker	similarity	4681	4744	24.1	+	.	ID=RepeatMaskerFeat.Azfi_s4733_4681-4744;Name=Motif:(CGCCGA)n
		Azfi_s4737	RepeatMasker	similarity	5482	5530	13.0	-	.	ID=RepeatMaskerFeat.Azfi_s4737_5482-5530;Name=Motif:Gypsy-64_PAb-I

		''')
	sys.exit(0)

args = sys.argv

if len(args) == 1:
	help()

