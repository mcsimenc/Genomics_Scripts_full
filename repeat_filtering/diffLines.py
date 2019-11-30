#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		diffLines file1 file2 [file3 [file4 [...]]]

		Description:
		------------
		Outputs lines that are present in file1 but not present in any other file. Sequentially stores each file in memory temporarily.

		Options:
		------------
		-h	Output this help

		''') 

	sys.exit(0)


if '-h' in sys.argv or len(sys.argv) < 3:
	help()

# This function compares a pair of files
#Determines which lines are in file1 and not in file2. Stores non-redundant lines from file2
#in memory and iterates through file1, asking if each line is in file2. If not, that line is
#output to stdout.
# diffLines.py file1 file2 > output.stdout

#def diffLines(file1, file2):
#
#	with open(file2) as f2:
#
#		file2set = set(f2.read().split('\n'))
#
#	with open(file1) as f1:
#
#		for line in f1:
#			if line.rstrip('\n') not in file2set:
#				print(line.rstrip('\n'))

def diffLines(file1, *args):

	with open(file1) as f1:

		diffSet = set(f1.read().split('\n'))

	for nextFile in args[0]:

		with open(nextFile) as f:

			diffSet.difference_update(set(f.read().split('\n')))

	for line in diffSet:

		print(line)

diffLines(sys.argv[1], sys.argv[2:])
