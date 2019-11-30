#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		python3 ./extract_fasta_seqs.py [fasta_file] [out_file] [options]

		Description:
		------------
		Outputs a file [out_file] in FASTA format containing the sequences derived
		from [fasta_file] corresponding to the names given in [seq_list].

		Options:
		------------
		-v	 	Inverse. Select all except seqs in seq_list

		-pattern <str>	Select sequences that contain <str> as a substring
				of the header.

		-batch		Extract matches to each seq in seq_list to separate
				files.

		-seq_list	List of sequence identifiers

		-n		 Write non-sequence non-header lines
				(for non-fasta_files with fasta-like headers)
		
		''')
	sys.exit(0)


args = sys.argv

inverse = False
if '-v' in args:
	inverse = True

if "-help" in args or "-h" in args or len(args) < 4:
	help()

# Input fasta
fasta_file = open(args[1])
# file to write to
out_file = open(args[2],"w")
# list of sequences to keep or remove
if '-seq_list' in args:
	seq_list = open(args[args.index('-seq_list')+1])

# will contain sequences to keep or remove
	seq_set = set()

	for seq in seq_list:
		seq_set.add(seq.strip())


if '-pattern' and '-batch' in args:
	for pattern in seq_set:
		current_outfile = '{0}.{1}.fasta'.format(outfile, pattern)
		for line in fasta_file:
			if line.startswith(">"):
				match = 0
				seqname = line.strip()[1:]
				if pattern in seqname:
					match = 1
					current_outfile.write(line)
				else:
					continue
			else:
				if match == 1:
					current_outfile.write(line)

				else:
					continue
		fasta_file.seek(0)

elif '-seq_list' in args:
	match = 0
	for line in fasta_file:
		if line.startswith(">"):
			match = 0
			seqname = line.strip()[1:]
			if '-v' in args:
				if '-pattern' in args:
					print("-pattern is not made to work with -v yet...")
					sys.exit()


				else:
					if seqname not in seq_set:
						out_file.write(line)
						match = 1
					else:
						seq_set.remove(seqname)
			elif '-v' not in args:
				if '-pattern' in args:
					for pattern in seq_set:
						if pattern in line:
							out_file.write(line)
							match = 1
							break
				else:
					if seqname in seq_set:
						match = 1
						out_file.write(line)
						seq_set.remove(seqname)
		# For nucleotide only
		#elif line[0] in 'ATCGN' and line[1] in 'ATCGN' and line[2] in 'ATCGN':
		# For protein or nucleotide
		else:
			if match == 1:
				out_file.write(line)
			elif match == 0:
				pass

		#else:
		#	if '-p' in args and match == 1:

		#			out_file.write(line)
		#	else:
		#		continue

	if not '-pattern' in args:
		if not seq_set == set():
			print('These seqences were not found:')
			for seq in seq_set:
				print(seq)
