#!/usr/bin/env python3 

#this script will extract period size copy number indices and sequence as a single line.
#ex: Azfi, 455,5465,23,34,ATCGTAGCGATAGCGCGATATAAV

import sys

args= sys.argv

for d in args[1:]:
	foundcons= False
	sequence= False
	seq= ""
	period= ""
	fl= open(d)
	for line in fl:
		line= line.strip()
#to make line Sequence appear
		if line.startswith("Sequence"):
			sequence= line.split(" ")
#to make line Indices
		if line.startswith("Indices"):
			indices= line.split(" ")
		if line.startswith("Period"):
			period= line.split(" ") 
		if line.startswith("Consensus"):
			foundcons= True
	#       elif foundcons== True:          
	#               seq= seq+line
	#elif line == "" and foundcons== True:
		elif line.startswith("Left"):
			foundcons= False
			print (sequence[1]+","+indices[1]+","+indices[4]+","+period[2]+","+period[5]+","+seq)
			seq= ""
		elif foundcons== True:
			seq= seq+line


