#!/usr/bin/env python3
# quick script to count the number of gene models from the gff file

import sys

args = sys.argv
in_fl = open(args[1])

models = set()
in_fl.readline()
for line in in_fl:
	models.add(line.split()[-1])

print(len(models))
