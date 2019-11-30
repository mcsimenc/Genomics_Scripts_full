#!/usr/bin/env python3

import sys


def help():
	print('''
		Usage:
		------------
		report_fasta_duplicates.py [fasta_file]

		Description:
		------------
		Reports sequence names that appear more than twice. For Sequence names that appear
		twice, reports whether the sequences are identical.
		
		''')
	sys.exit(0)

args = sys.argv

if '-h' in args or len(args) !=2:
	help()


# this dictionary will have all the sequence names and sequences in it. so the whole fasta file will get loaded into memory, which for huge fasta files wouldn't be good.
sequences = {}
duplicate_sequences = {}

duplicate = False

more_than_duplicates = []
triplicate = False

# open the fasta file. it should be the first argument after the name of this script on the command line
with open(args[1]) as infl:
	# this is to save the name of the current fasta sequence because the sequence is on different lines than the header
	current_sequence = ''
	
	# go through the file line by line
	for line in infl:
		# take out the sequence name
		if line.startswith('>'):
			triplicate = False
			# save the name as the current sequence
			current_sequence = line.strip()[1:]

			# this will try to access the key for this sequence name from the dictionary. if it is is not there, Python will return a KeyError, and will execute the code in the except block.
			try:
				sequences[current_sequence]
			except KeyError:
				# add the sequence name to the dictionary as a key with its value being an empty string. we'll add the sequences this empty string
				sequences[current_sequence] = ''
				duplicate = False
			else:
				try:
					duplicate_sequences[current_sequence]
				except KeyError:
					duplicate_sequences[current_sequence] = ''
					duplicate = True
				else:
					triplicate = True
					more_than_duplicates.append(current_sequence)
		else:
			if triplicate:
				continue

			elif duplicate:
				duplicate_sequences[current_sequence] += line.strip()
			else:
				# Add the sequence to the current sequence
				sequences[current_sequence] += line.strip()


print("These sequence names appear more than twice:")
print("-------------------------------------------")
for seqname in more_than_duplicates:
	print(seqname)

print('\n')

for name, seq in duplicate_sequences.items():
	if sequences[name] == duplicate_sequences[name]:
		print("Duplicate name, identical sequence:\t{0}".format(name))
	else:
		print("Duplicate name, different sequence:\t{0}".format(name))
