#!/usr/bin/env python3

#this program takes gff files and extracts sequence ID and consensus sequence by setting boundaries for copy number, lower bound period size and 
#upper bound period size.
#Ex. namefile.gff 5 200 340
#5= minimum copy number
#200= lower bound period size
#340= upper boumd period size
#this script won't work to convert a FASTA file without parameters.


import sys

args= sys.argv

fl= open(args[1])
cn= float(args[2])
le= int(args[3])
ue= int(args[4])


for line in fl:
	line= line.strip().split()
#to pull up the ID only
	ID= line[8].split(";")
	PC= ID[1].split("=")
	P= int(PC[1])
	CN= ID[2].split("=")
	C= float(CN[1])
	#print (P)
	FILEID= ID[0].split("=")
	SEQUENCE= ID[3].split("=")
	A=FILEID[1]
	B=SEQUENCE[1]
#this part allows the script to create a fasta file if requested with -f or it will create a gff file if you input -g.
	if "-f" in args:
		if C >= cn and le <= P and ue >= P:
			print(">"+A,"\n"+B)
	if "-g" in args:
		if C>=cn and le <= P and ue >=P:
			print(line)
