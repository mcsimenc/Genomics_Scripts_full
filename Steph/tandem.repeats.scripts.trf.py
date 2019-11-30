#!/usr/bin/env python3 

import sys

args= sys.argv

for d in args[1:]:
	foundcons= False
	seq= ""
	period= ""
	fl= open(d)
	for line in fl:
		line= line.strip()
		if line.startswith("Period"):
			period= line.split(" ") 
		if line.startswith("Consensus"):
			foundcons= True
	#	elif foundcons== True: 		
	#		seq= seq+line
		#elif line == "" and foundcons== True:
		elif line.startswith("Left"):
			foundcons= False
			print (period[2]+","+period[5]+","+seq)
			seq= ""
		elif foundcons== True:
			seq= seq+line
