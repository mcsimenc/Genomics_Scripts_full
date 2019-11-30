#!/usr/bin/env python3

# METHOD ONE W/O CSV

#set declarations
# import re
# import sys
# file = sys.argv[1]

#1 read the lines
# with open(file, 'r') as gff:
# 	for line in gff:
		
#2 split the lines from the right with the separator as a tab and return only the right most line

#3 split the line along the KEY=VALUE and ";" separators

#4.1 if a string starts with ID= and ends with ;, or starts with ID= and ends at the line, append a tab that to the end of the line, or else if the string contains nothing like that, append a tab and then another tab

#5 continue for:
# Name=
# Alias=
# Parent= 
# Target=
# Gap=
# Derives_from = 
# Note= 
# Dbxref=
# Ontology_term=
# Is_circular=

#6 find all cases where a string is not contained within the parameters (in order to catch any potential tag=value pairs not mentioned





# METHOD TWO WITH CSV

#set declarations
# import re
# import sys
# import csv
# file = csv.reader(open(sys.argv[1], 'rb'), delimiter='\t')
# #1 open file
# # with open(file) as gff:
# for i in range(20):
# 	print file.next()
#2 declare columns
#3 declare 9th column as string
#4 append relevant strings into rows, or append what goes into gff files


# METHOD THREE: MATT METHOD
import re
import sys
import csv

def help():
	print('''
		Usage:
		------------
		gff_expandCol9_forMySQLimport.py [input.gff] 

		Description:
		------------
		Converts a GFF3 file to a tab-delimited file (on stdout) with
		the same information, but with each key-value pair from the
		input.gff expanded into it's own column.
		''')
	sys.exit(0)

if len(sys.argv) != 2:
	help()

#file = csv.reader(open(sys.argv[1], 'rb'), delimiter='\t')
file = open(sys.argv[1], 'r')
attributes = set()
gffdict = {}
linenum = 0
#1 for loop through the gff file
for line in file:
	# skip lines that are commented out
	if line.startswith('#'):
		continue

	contents = line.strip().split('\t')
#2 for loop through the result of line.split(';')
	linenum += 1
	try:
		col9list = contents[8].split(';')
	except IndexError:
		print(line, file=sys.stderr)
		continue
#3 split the key-value pairs using pair.split('=')
	gffdict[linenum] = {}
	gffdict[linenum]['gff'] = contents[0:8]
	for pair in col9list:
#4 put the first item in the result of pair.split('=') in a set you already made
		attribute = pair.split('=')
		AttributeKey = attribute[0].strip('_')
		AttributeValue = attribute[1]
		attributes.add(AttributeKey)
		gffdict[linenum][AttributeKey] = AttributeValue

# Convert attribute set to list for looping through to print attributes out in order
attrList = sorted(list(attributes))

# Print headers for columns 1-8
print('seqid\tsource\ttype\tstart\tend\tscore\tstrand\tphase', end='')

# Print headers for attributes column
for attr in attrList:
	print('\t', end='')
	print(attr, end='')
print('\n', end='')

# Print data
for i in range(1, len(gffdict)+1):
	# Print columns 1-8
	print('\t'.join(gffdict[i]['gff']), end='')

	# Print attributes. If no attribute print a period
	for attr in attrList:
		print('\t', end='')
		try:
			print(gffdict[i][attr], end='')
		except KeyError:
			print('.', end='')

	print('\n', end='')
	
	
	
#5 put the second item in the result of pair.split('=') in a nested dictionary
# you shoud have a variable that's a number that increments by one every time the outer 
# loop does an iteration, that way you get a number corresponding to whatever line you're 
# on. This number will be the key for that line's data in the outer dictionary. It's a 
# nested dictionary because the values of these keys are dictionaries
