#!/usr/bin/env python3


import sys
import re


def help():
	print('''
		Usage:
		------------
		summarize_repeat_masker_gff.py <input_gff3>

		Description:
		------------
		Takes a GFF3 from RepeatMasker and writes two tables,
		a full and a short.

		The short combines features with names into these categories:
		1. Simple - things whose names are just A, T, C, or G
		2. Gypsy
		3. Copia
		4. hAT
		5. Other


		Options:
		------------
		-db	EMBL format Repbase DB. If -db extra information will be added to the output table
		-bed	BED input format, as is output from bedtools subtract, instead of GFF3
		
		''')
	sys.exit(0)


if len(sys.argv) < 2 or '-h' in sys.argv:
	help()


#Target "Motif:(TTTGAA)n"
#Target "Motif:LSU-rRNA_Ath"

# BED EXAMPLE FROM MAKER AND RM

#Azfi_s0001	0	565	Azfi_s0001:hit:191:1.3.0.0	2.94e+03	+	repeatmasker	match	.	ID=Azfi_s0001:hit:191:1.3.0.0;Name=species:deg7180000005503|quiver|genus:Unspecified;Target=species:deg7180000005503|quiver|genus:Unspecified 1014 1371 +
#Azfi_s0001	615	625	Azfi_s0001:hit:192:1.3.0.0	1.32e+04	+	repeatmasker	match	.	ID=Azfi_s0001:hit:192:1.3.0.0;Name=species:SSU-rRNA_Ath|genus:rRNA;Target=species:SSU-rRNA_Ath|genus:rRNA 86 1891 +

#Azfi_s4735	5031	5092	.	27.0	+	RepeatMasker	similarity	.	Target "Motif:(GCC)n" 1 60
#Azfi_s4736	5326	5389	.	19.3	+	RepeatMasker	similarity	.	Target "Motif:Gypsy-33_PAb-LTR" 165 233


target_re_pattern = re.compile('Target "Motif:(.+)"')

target_re_pattern_repeatmasker = re.compile('Target=(.+?)\s') # Matches repeatmasker and repeatrunner lines in maker gff

name_simple_pattern = re.compile('\([ATCG]+\)n')

target_re_pattern_makerlines = re.compile('Name=species:(.+?)\|genus')
#ID=Azfi_s0001:hit:224:1.3.0.0.RVT_1.1;Name=RM_24140_rnd-4_family-214_bestblasthit_L1-3_SMo_L1_Selaginella_moellendorffii.aln_len_281.evalue_3e-111.RVT_1.1;Parent=Azfi_s0001:hit:224:1.3.0.0;aa_seq=KKWRPISILNTIYKIYAKVLSLRMQPLLNDIIHKLQTNFMQKRSIFYNIFMFWELTTLAKEKDEDLAVLLLDFEMAYDRVDWCFLEEVMLQLGFPMAWVVAVRALYKNASSFVYVTGKVDTPFSISRLVRQGCPLAPFIYLLITEAFHIMFFNNHAL%2AIKGLQWGVDNKQVLDNEFANDTTLY;E-value=2.3e-22

#short_names_set = set(['Gypsy', 'Copia', 'hAT'])


summary_dct_full = {}
summary_dct_short = {}
summary_dct_supershort = {}

input_file_name = sys.argv[1]

repbase_db = {}

if '-db' in sys.argv:

	with open(sys.argv[sys.argv.index('-db') + 1]) as repbase_db_fl:

		name = ''

		for line in repbase_db_fl:

			if line.startswith('ID'):

				name = line.strip().lstrip('ID ').split()[0]

				repbase_db[name] = ''

			elif line.startswith('DE'):

				repbase_db[name] += line.strip().lstrip('DE ')

			elif line.startswith('KW'):

				repbase_db[name] += line.strip().lstrip('KW ')


bestblasthit_pat = re.compile('bestblasthit_(.+)\.aln_len')
#Azfi_s0001	repeatmasker	match	2482	3175	4.03e+03	+	.	ID=Azfi_s0001:hit:193:1.3.0.0;Name=RM_24141_rnd-3_family-26_bestblasthit_SSU-rRNA_Lvi.aln_len_318.evalue_0.0;Target=species:RM_24141_rnd-3_family-26|genus:Unspecified 1723 2418 +


# read in data
with open(input_file_name) as in_fl:

	for line in in_fl:

		if not line.startswith('#'):

			fields = line.split('\t')

			if '-bed' in sys.argv:
				start = int(fields[1])
				end = int(fields[2])
				length = end - start
				if fields[7] == 'pfam_domain':
					continue
				if fields[7] == 'match': # MAKER output lines

					if 'bestblast' in fields[9]:
						name = re.search(bestblasthit_pat, fields[9]).group(1)
				#	elif 'genus:Unspecified' in fields[9]:
				#		name = 'Unspecified'
					elif 'genus:Simple' in fields[9]:
						name = 'Simple'
					else:
						#name = re.search(target_re_pattern_makerlines, fields[9]).group(1)
						try:
							name = re.search(target_re_pattern, fields[9]).group(1)
						except AttributeError:
							name = re.search(target_re_pattern_repeatmasker, fields[9]).group(1)

					supershort_name = None

				else: # RepeatMasker lines
					name = re.search(target_re_pattern, fields[9]).group(1)
					supershort_name = None
			else: # Gff input
				start = int(fields[3])
				end = int(fields[4])
				length = end - start + 1

				if 'Simple_repeat' in fields[8]:
					name = 'Simple'
				elif 'bestblast' in fields[8]:
					name = re.search(bestblasthit_pat, fields[8]).group(1)
				elif '|genus:Unspecified;' in fields[8]:
					name = 'Unspecified'
				else:

					try:
						name = re.search(target_re_pattern, fields[8]).group(1)
					except AttributeError:

						try:
							name = re.search(target_re_pattern_makerlines, fields[8]).group(1)
						except AttributeError:
							try:
								name = re.search(target_re_pattern_repeatmasker, fields[8]).group(1)
							except AttributeError:
								name = re.search(bestblasthit_pat, fields[8]).group(1)

				supershort_name = None



			try:

				repbase_db[name] # throws an KeyError, always the case if not -db. If name is not in the repbase db given by -db we want to execute the following except block anyways

				lowercase_name = name.lower()
				repbase_db_entry_lowercase = repbase_db[name].lower()

				if re.search(name_simple_pattern, name):
					short_name = 'Simple'
				elif name == 'Simple':
					short_name = 'Simple'
				elif name == 'Unspecified':
					short_name = 'Unspecified'
				elif 'copia' in lowercase_name or 'copia' in repbase_db_entry_lowercase or 'shacop' in lowercase_name:
					short_name = 'Copia'
				elif 'gypsy' in lowercase_name or 'gypsy' in repbase_db_entry_lowercase or 'ogre' in lowercase_name or 'ogre' in repbase_db_entry_lowercase:
					short_name = 'Gypsy'
				elif 'helitron' in lowercase_name or 'helitron' in repbase_db_entry_lowercase:
					short_name = 'Helitron'
				elif 'mariner' in lowercase_name or 'mariner' in repbase_db_entry_lowercase or 'tc1' in lowercase_name:
					short_name = 'Mariner'
				elif 'mudr' in lowercase_name or 'mudr' in repbase_db_entry_lowercase or 'mutator' in repbase_db_entry_lowercase:
					short_name = 'MuDR'
				elif 'harb' in lowercase_name or 'harbinger' in repbase_db_entry_lowercase:
					short_name = 'Harbinger'
				elif 'trna' in lowercase_name:
					short_name = 'tRNA'
				elif 'rrna' in lowercase_name or 'rrna' in repbase_db_entry_lowercase:
					short_name = 'rRNA'
				elif 'snrna' in lowercase_name or 'snrna' in repbase_db_entry_lowercase:
					short_name = 'snRNA'
				elif 'sine' in lowercase_name:
					short_name = 'Other_SINE'
				elif 'cacta' in repbase_db_entry_lowercase or 'enspm' in lowercase_name or 'enspm' in repbase_db_entry_lowercase or 'cacta' in lowercase_name:
					short_name = 'EnSpm/CACTA'
				elif 'caulimovir' in repbase_db_entry_lowercase:
					short_name = 'Caulimovirus'
				elif 'microsatellite' in repbase_db_entry_lowercase or 'minisat' in lowercase_name:
					short_name = 'Microsatellite'
				elif 'hat' in lowercase_name or 'hAT' in repbase_db[name]:
					short_name = 'hAT'
				elif 'novosib' in repbase_db_entry_lowercase:
					short_name = 'Novosib'
				elif 'penelope' in lowercase_name or 'penelope' in repbase_db_entry_lowercase:
					short_name = 'Penelope'
				elif 'polinton' in lowercase_name or 'polinton' in repbase_db_entry_lowercase:
					short_name = 'Polinton'
				elif 'maverick' in lowercase_name or 'maverick' in repbase_db_entry_lowercase:
					short_name = 'Polinton'
				elif 'piggybac' in lowercase_name or 'piggybac' in repbase_db_entry_lowercase:
					short_name = 'PiggyBac'
				elif 'RTEX' in repbase_db[name] or 'rtex' in lowercase_name:
					short_name = 'RTEX'
				elif 'RTE' in repbase_db[name] or 'rte' in lowercase_name:
					short_name = 'RTE'
				elif 'jock' in lowercase_name or 'cr1' in lowercase_name or 'crack' in lowercase_name or 'daphne' in lowercase_name or 'jock' in repbase_db_entry_lowercase or 'crack' in repbase_db_entry_lowercase or 'daphne' in repbase_db_entry_lowercase or 'cr1' in repbase_db_entry_lowercase:
					short_name = 'Jockey'
				elif 'line' in lowercase_name:
					short_name = 'Other_LINE'
				elif 'dirs' in lowercase_name:
					short_name = 'DIRS'
				elif 'dada' in lowercase_name or 'dada' in repbase_db_entry_lowercase:
					short_name = 'DADA'
				elif 'bel' in lowercase_name:
					short_name = 'BEL'
				elif 'L1' in repbase_db[name] or 'l1' in lowercase_name or 'tx1' in lowercase_name or 'tx1' in repbase_db[name]:
					short_name = 'L1'
				elif 'L2' in repbase_db[name] or 'l2' in lowercase_name:
					short_name = 'L2'
				elif 'erv' in lowercase_name:
					short_name = 'ERV'
				elif 'rep' in lowercase_name:
					short_name = 'REP'
				elif 'sola' in lowercase_name or 'sola' in repbase_db[name]:
					short_name = 'SOLA'
				elif 'satellite' in repbase_db_entry_lowercase or 'sat' in lowercase_name:
					short_name = 'Satellite'
				elif 'non-ltr retrotransposon' in repbase_db_entry_lowercase:
					short_name = 'Other_non-LTR_retrotransposon'
				elif 'dna transpos' in repbase_db_entry_lowercase or 'dna-' in lowercase_name or re.search('dna\d', lowercase_name):
					short_name = 'Other_DNA_transposon'
				elif 'ltr retrotranspos' in repbase_db_entry_lowercase or 'ltr' in lowercase_name or 'tto1' in lowercase_name or 'tnt1' in lowercase_name or 'tlc1' in lowercase_name or 'tcn1' in lowercase_name:
					short_name = 'Other_LTR_retrotransposon'
				elif 'unspecified' in lowercase_name:
					short_name = 'Unspecified'
				else:
					short_name = name
					supershort_name = 'Other'

				if not supershort_name == 'Other':
					supershort_name = short_name

			
			except KeyError: # runs if -db is not specified

				lowercase_name = name.lower()

				if re.search(name_simple_pattern, name):
					short_name = 'Simple'
				elif name == 'Simple':
					short_name = 'Simple'
				elif name == 'Unspecified':
					short_name = 'Unspecified'
				elif 'copia' in lowercase_name or 'shacop' in lowercase_name:
					short_name = 'Copia'
				elif 'gypsy' in lowercase_name or 'ogre' in lowercase_name:
					short_name = 'Gypsy'
				elif 'hat' in lowercase_name:
					short_name = 'hAT'
				elif 'helitron' in lowercase_name:
					short_name = 'Helitron'
				elif 'mariner' in lowercase_name or 'tc1' in lowercase_name:
					short_name = 'Mariner'
				elif 'mudr' in lowercase_name:
					short_name = 'MuDR'
				elif 'harb' in lowercase_name:
					short_name = 'Harbinger'
				elif 'penelope' in lowercase_name:
					short_name = 'Penelope'
				elif 'polinton' in lowercase_name:
					short_name = 'Polinton'
				elif 'piggybac' in lowercase_name:
					short_name = 'PiggyBac'
				elif 'trna' in lowercase_name:
					short_name = 'tRNA'
				elif 'rrna' in lowercase_name:
					short_name = 'rRNA'
				elif 'dada' in lowercase_name:
					short_name = 'DADA'
				elif 'sine' in lowercase_name:
					short_name = 'Other_SINE'
				elif 'enspm' in lowercase_name or 'cacta' in lowercase_name:
					short_name = 'EnSpm/CACTA'
				elif 'rtex' in lowercase_name:
					short_name = 'RTEX'
				elif 'rte' in lowercase_name:
					short_name = 'RTE'
				elif 'jock' in lowercase_name or 'cr1' in lowercase_name or 'crack' in lowercase_name or 'daphne' in lowercase_name:
					short_name = 'Jockey'
				elif 'line' in lowercase_name:
					short_name = 'Other_LINE'
				elif 'dirs' in lowercase_name:
					short_name = 'DIRS'
				elif 'bel' in lowercase_name:
					short_name = 'BEL'
				elif 'dna-' in lowercase_name or re.search('dna\d', lowercase_name):
					short_name = 'Other_DNA_transposon'
				elif 'ltr' in lowercase_name or 'tto1' in lowercase_name or 'tnt1' in lowercase_name or 'tlc1' in lowercase_name or 'tcn1' in lowercase_name or 'gag' in line or 'zf-CCHC' in line or 'DUF4219' in line or 'RVT' in line or 'Asp_protease' in line or 'RVP' in line:
					short_name = 'Other_LTR_retrotransposon'
				elif 'l1' in lowercase_name or 'tx1' in lowercase_name:
					short_name = 'L1'
				elif 'l2' in lowercase_name:
					short_name = 'L2'
				elif 'erv' in lowercase_name:
					short_name = 'ERV'
				elif 'rep' in lowercase_name:
					short_name = 'REP'
				elif 'sola' in lowercase_name:
					short_name = 'SOLA'
				elif 'sat' in lowercase_name:
					short_name = 'Satellite'
				elif 'minisat' in lowercase_name:
					short_name = 'Microsatellite'
				elif 'unspecified' in lowercase_name:
					short_name = 'Unspecified'
				else:
					short_name = name
					supershort_name = 'Other'


				if not supershort_name == 'Other':
					supershort_name = short_name


	#		if supershort_name == "Unspecified":
	#			print(name)
	#			print(line)

			# for long/full output
			if name in summary_dct_full:
				summary_dct_full[name]['count'] += 1
				summary_dct_full[name]['length'] += length
			else:
				summary_dct_full[name] = {'count':1, 'length':length}

			# for short output
			if short_name in summary_dct_short:

				summary_dct_short[short_name]['count'] += 1
				summary_dct_short[short_name]['length'] += length
			else:
				summary_dct_short[short_name] = {'count':1, 'length':length}

			# for supershort output
			if supershort_name in summary_dct_supershort:

				summary_dct_supershort[supershort_name]['count'] += 1
				summary_dct_supershort[supershort_name]['length'] += length
			else:
				summary_dct_supershort[supershort_name] = {'count':1, 'length':length}


# output full data
with open('{0}.summary_full'.format(input_file_name), 'w') as out_fl_full:

		if '-db' in sys.argv:
			# if -db
			out_fl_full.write('Name\tCount\tLength\tDescription\n')
			for name in summary_dct_full:
				try:
					out_fl_full.write('{0}\t{1}\t{2}\t{3}\n'.format(name, summary_dct_full[name]['count'], summary_dct_full[name]['length'], repbase_db[name]))
				except KeyError:
					out_fl_full.write('{0}\t{1}\t{2}\t{3}\n'.format(name, summary_dct_full[name]['count'], summary_dct_full[name]['length'], 'No description found. Name may not exactly match ID in rebpase EMBL'))

		else:
			# default, if -db is not specified
			out_fl_full.write('Name\tCount\tLength\n')
			for name in summary_dct_full:
				out_fl_full.write('{0}\t{1}\t{2}\n'.format(name, summary_dct_full[name]['count'], summary_dct_full[name]['length']))


with open('{0}.summary_short'.format(input_file_name), 'w') as out_fl_short:

		if '-db' in sys.argv:
			# if -db
			out_fl_short.write('Name\tCount\tLength\tDescription\n')
			for name in summary_dct_short:
				try:
					out_fl_short.write('{0}\t{1}\t{2}\t{3}\n'.format(name, summary_dct_short[name]['count'], summary_dct_short[name]['length'], repbase_db[name]))
				except KeyError:
					out_fl_short.write('{0}\t{1}\t{2}\t{3}\n'.format(name, summary_dct_short[name]['count'], summary_dct_short[name]['length'], 'No description found. Name may not exactly match ID in rebpase EMBL'))
		else:
			# default, if -db is not specified
			out_fl_short.write('Name\tCount\tLength\n')
			for name in summary_dct_short:
				out_fl_short.write('{0}\t{1}\t{2}\n'.format(name, summary_dct_short[name]['count'], summary_dct_short[name]['length']))


with open('{0}.summary_supershort'.format(input_file_name), 'w') as out_fl_supershort:

		if '-db' in sys.argv:
			# if -db
			out_fl_supershort.write('Name\tCount\tLength\tDescription\n')
			for name in summary_dct_supershort:
				try:
					out_fl_supershort.write('{0}\t{1}\t{2}\t{3}\n'.format(name, summary_dct_supershort[name]['count'], summary_dct_supershort[name]['length'], repbase_db[name]))
				except KeyError:
					out_fl_supershort.write('{0}\t{1}\t{2}\t{3}\n'.format(name, summary_dct_supershort[name]['count'], summary_dct_supershort[name]['length'], 'No description found. Name may not exactly match ID in rebpase EMBL'))
		else:
			# default, if -db is not specified
			out_fl_supershort.write('Name\tCount\tLength\n')
			for name in summary_dct_supershort:
				out_fl_supershort.write('{0}\t{1}\t{2}\n'.format(name, summary_dct_supershort[name]['count'], summary_dct_supershort[name]['length']))
