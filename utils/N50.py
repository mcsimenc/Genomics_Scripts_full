#!/usr/bin/env python3

import sys

def help():
	print('''
		N50.py <file> [-n25]

		assumes the input is a list of numbers

		-n25	calculate N25 instead
		''')
	sys.exit(0)

if '-h' in sys.argv:
	help()


lengths = sorted([ int(i) for i in open(sys.argv[1]).read().strip().split('\n') ], reverse=True)
total_length = sum(lengths)


running_sum = 0
if '-n25' in sys.argv:
	for i in range(len(lengths)):
		running_sum += lengths[i]
		if running_sum >= total_length/4:
			print('length\t{0}'.format(lengths[i]))
			print('seqs\t{0}'.format(i+1))
			break

else:
	for i in range(len(lengths)):
		running_sum += lengths[i]
		if running_sum >= total_length/2:
			print('length\t{0}'.format(lengths[i]))
			print('seqs\t{0}'.format(i+1))
			break
