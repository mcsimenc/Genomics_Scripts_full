#!/usr/bin/env python3

import sys
import re

def help():
	print('''
		Usage:
		------------
		merge_gff3s.py

		Description:
		------------
		Written specifically to (1) merge hmmer hmmsearch results
		gff as created with the Mgkit program hmmer2gff, when hmmsearch
		was performed on a set of sequences extracted from a
		MAKER-P-generated GFF3 file using bedtools getfasta
		(bedtools getfasta puts the 0-based coordinates for each feature
		in the sequence identifier in the resulting FASTA file, and
		this script uses that information), with the original MAKER-P
		GFF3 file. Basically this script translates coordinates from
		subfeatures back to the original system.

		For example, this identifier (field 1 in hmmsearch gff):

			Sacu_v1.1_s0225:13066-13249(+)

		corresponds to the line in the MAKER-P GFF3 file from which
		it was extracted that has in the 1st, 3rd, and 4th fields:

			Sacu_v1.1_s0225, 13067, 13249

		The start coord is different because GFF3 is 1-based and
		the coord in the seq id made by bedtools is 0-based, like
		BED format.

		A subfeature starting at position 1 of this feature in the
		hmmsearch gff is actually at position 13067 in the MAKER-P
		gff. If it ends at position 10 in the hmmsearch gff, it's
		end in the MAKER gff is 10 + 13067 - 1. Since the start coord
		in the bedtools getfasta generated seq id is 0-based, the
		translation used by this script is:

			MAKER_start = seqid_start + hmmer_start
			MAKER_end = seqid_start + hmmer_end


		This script also adds "Parent" key to the attributes field
		in the output GFF3 that is the value of the "Name" key in the
		MAKER GFF3 for this feature.

		Options:
		------------
		-h		display this help.

		-hmmer		hmmsearch GFF3 file. Can't be used with -blast

		-maker		maker GFF3 file

		-evalue		maximum evalue to accept. Default 1

		-blast		BLAST output to merge, table format, subject field
				has the new annotation and query field has the
				value of the Name attribute in the -maker gff.
				Can't be used with -hmmer.

		-bedkey		Use this when the query names in the blast output
				are like bedtools getfasta -s output:

					scaf:start-end(+)

				where start and end are 0-based. -hmmer assumes -bedkey.
		''')
	sys.exit(0)


# Get parameters
args = sys.argv

if '-h' in args or len(args) < 5:
	help()
if '-blast' in args and '-hmmer' in args:
	help()


if '-evalue' in args:
	evalue = float(args[args.index('-evalue') + 1])
else:
	evalue = 1







if '-hmmer' in args:

	hmmer_dict = {} # dict will have keys that are compiled regex expressions that should match one line in the maker gff and values that will be the new gff line to print
	hmmer_gff = args[args.index('-hmmer') + 1]

	with open(hmmer_gff) as in_fl:

		scaf_pat = re.compile('(^.+):')
		start_pat = re.compile(':(\d+)-')
		end_pat = re.compile('-(\d+)')
		aa_seq_pat = re.compile('aa_seq="(.+?)"')
		domain_name_pat = re.compile('name="(.+?)"')

		for line in in_fl:

			if not line.startswith('#'):

				fields = line.split('\t')
				score = float(fields[5])

				if score > evalue:
					continue
				else:
					score = str(score)

				seqid = fields[0]
				scaf = re.search(scaf_pat, seqid).group(1)
				bed_start = int(re.search(start_pat, seqid).group(1))
				bed_end = re.search(end_pat, seqid).group(1)
				maker_line_info = (scaf, str(bed_start+1), bed_end)
				source = fields[1]
				Type = fields[2]
				subfeat_start = int(fields[3])
				subfeat_end = int(fields[4])
				maker_start = str(bed_start + subfeat_start)
				maker_end = str(bed_start + subfeat_end)
				strand = fields[6]
				phase = fields[7]
				attr = fields[8]
				aa_seq = re.search(aa_seq_pat, attr).group(1)
				domain = re.search(domain_name_pat, attr).group(1)
			
				new_line = [scaf, source, Type, maker_start, maker_end, score, strand, phase, [aa_seq, domain] ]

				if maker_line_info in hmmer_dict:
					hmmer_dict[maker_line_info].append(new_line)
				else:
					hmmer_dict[maker_line_info] = [ new_line ]


# Example line from hmmsearch generated GFF3
#Sacu_v1.1_s0093:477988-478202(+)	HMMER	pfam_domain	66	212	1.5e-12	-	2	aa_from="1";aa_seq="YHGVRRRSWGKWVSEIREPKKKSRIWLGSYPTPEMAARAYDVAALCLKG";aa_to="49";bitscore="51.7";db="CUSTOM";evalue="1.5e-12";frame="r2";gene_id="AP2";name="AP2";uid="6248b64b-3978-44bd-bd7f-df747caad9de"

# FOR DEBUGGING
#n = 0
#for k in hmmer_dict:
#	n += len(hmmer_dict[k])
#print(n)

if '-blast' in args:

	blast = args[args.index('-blast') + 1]
	blast_dict = {}

	if '-bedkey' in args:

		bedkey_scaf_pat = re.compile('^(.+?):')
		bedkey_start_pat = re.compile(':(\d+?)-\d')
		bedkey_end_pat = re.compile(':\d+-(\d+)')

	with open(blast) as in_fl:

		for line in in_fl:

			if not line.startswith('#'):

				# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score

#Sacu_v1.1_s0093	repeatmasker	match	477989	478202	506	+	.	ID=Sacu_v1.1_s0093:hit:80082:1.3.0.4;Name=species:RM_9634_rnd-5_family-3542|genus:Unspecified;Target=species:RM_9634_rnd-5_family-3542|genus:Unspecified 20 221 +

				fields = line.split('\t')
				query = fields[0]
				subject = fields[1]
				aln_len = fields[3]
				evalue = fields [10]

				if '-bedkey' in args:

					scaf = re.search(bedkey_scaf_pat, query).group(1)
					gff_start = str(int(re.search(bedkey_start_pat, query).group(1)) + 1)
					end = re.search(bedkey_end_pat, query).group(1)
					query = (scaf, gff_start, end)

				if query in blast_dict:
					print('Multiple identical queries in blast input table', file=sys.stderr)
					print(query, file=sys.stderr)

				else:
					blast_dict[query] = [subject, aln_len, evalue]


				


maker_gff = args[args.index('-maker') + 1]
			
with open(maker_gff) as in_fl:

	name_pat = re.compile('Name=(.+?);')
	id_pat = re.compile('ID=(.+?);')
	blast_name_pat = re.compile('Name=species:(.+?)\|genus')

	for line in in_fl:

		line = line.strip()

		if not line.startswith('#'):

			fields = line.split('\t')
			scaf = fields[0]
			start = fields[3]
			end = fields[4]

			if '-hmmer' in args:

				hmmer_dict_key = (scaf, start, end)

				if hmmer_dict_key in hmmer_dict:


					attr = fields[8]
					ID = re.search(id_pat, attr).group(1)
					name = re.search(name_pat, attr).group(1)
					feat_nums = {}

					for new_line in hmmer_dict[hmmer_dict_key]:

						aa_seq = new_line[-1][0]
						domain = new_line[-1][1]

						if domain in feat_nums:
							feat_nums[domain] += 1
							domain_num = '{0}.{1}'.format(domain, feat_nums[domain])
						else:
							feat_nums[domain] = 1
							domain_num = '{0}.{1}'.format(domain, feat_nums[domain])

						new_ID = '{0}.{1}'.format(ID, domain_num)
						new_name = '{0}.{1}'.format(name, domain_num)
						new_attr = 'ID={0};Name={1};Parent={2};aa_seq={3};E-value={4}'.format(new_ID, new_name, ID, aa_seq, new_line[5])

						new_line[-1] = new_attr

						print('\t'.join(new_line))

			if '-blast' in args:

				if 'bestblasthit' in line:

					print(line)
					continue

				if '-bedkey' in args:

					feat_name = (scaf, start, end)

				else:

					try:
						feat_name = re.search(blast_name_pat, line).group(1)

					except:
						print(line)
						continue

				

				if feat_name in blast_dict:

					blasthit = blast_dict[feat_name][0]
					aln_len = blast_dict[feat_name][1]
					evalue = blast_dict[feat_name][2]
					attr = fields[8].split(';')

					if '-bedkey' in args:
						feat_name = re.search(blast_name_pat, line).group(1)

					new_attr = [ item if not item.startswith('Name') else 'Name={0}_bestblasthit_{1}.aln_len_{2}.evalue_{3}'.format(feat_name, blasthit, aln_len, evalue) for item in attr ]
					fields[8] = ';'.join(new_attr)
					new_line = '\t'.join(fields)
					print(new_line)

				else:

					print(line) # these lines don't have matches in the blast results table


			else:

				print(line)
				


# Example MAKER gff line
#Sacu_v1.1_s0093	repeatmasker	match	477989	478202	506	+	.	ID=Sacu_v1.1_s0093:hit:80082:1.3.0.4;Name=species:RM_9634_rnd-5_family-3542|genus:Unspecified;Target=species:RM_9634_rnd-5_family-3542|genus:Unspecified 20 221 +
