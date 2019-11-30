#!/usr/bin/env python3 

#this script will transfor a trf file into a gff file.
#ex: "Azfi_s1000      trf     tandem_repeat   29564   29796   466     .       .       ID=Azfi_s1000_23;period=116;copynumber=2.0;sequence=GGACCTTTCAAGCAAGCCGCAACCCGAACAGGTAATAGGTATATCATCGTGGCCATGGACTA"


import sys

args= sys.argv
id=1
for d in args[1:]:
	seqID= ""
	source= "trf"
	type= "tandem_repeat"
	strand= "."
	phase= "."
	foundcons= False
	seq= ""
	period= ""
	foundfound= False
	fl= open(d)
	for line in fl:
		line= line.strip()
#to make line Sequence appear
		if line.startswith("Sequence"):
			sequence= line.split(" ")
			seqID= sequence[1]
		
#to make line Indices appear
		if line.startswith("Indices"):
			LINE= line.split(" ")
			INDICES= LINE[1].split("--")
			start= INDICES[0]
			end= INDICES[1]
			score= LINE[4]			
		if line.startswith("Period"):
			period= line.split(" ") 
		if line.startswith("Consensus"):
			foundcons= True
		elif line.startswith("Left"):
			foundcons= False
			#seq= ""
		elif foundcons== True:
			seq= seq+line
		if line.startswith("Found") and foundfound== False:
			foundfound= True

		elif line.startswith("Found") and foundfound== True or line.startswith("Done"):		
			

			attributes=  "ID={0}_{4};period={1};copynumber={2};sequence={3}".format(sequence[1],period[2],period[5],seq,id)
			print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}".format(seqID,source,type,start,end,score,strand,phase,attributes))
			seq= ""
			id+=1
