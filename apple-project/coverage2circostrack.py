#!/usr/bin/env python3

import sys

def help():
	print('''
 Usage:
 ------------
 coverage2circostrack.py <genomecov_output>
 
 Input:
 ------------
 Takes the output of bedtools genomecov -ibam <bam> -d:

 chr	pos	doc

 Output:
 ------------
 A line track for Circos. If a scaffold ends before, the final
 binsize may be smaller than the binsize asked for. This can result
 in more extreme values for average depth of coverage.

 chr 	start	end	average_depth_of_coverage

 Options:
 ------------
 -bin <int>	bp in bin size. Default (100000)
 ''')

if __name__ == '__main__':
	args = sys.argv
	if len(args) < 2:
		help()
		sys.exit()
	if '-bin' in args:
		binsize = int(args[args.index('-bin')+1])
	else:
		binsize = 100000
	with open(args[1],'r') as inFl:
		ct = 0
		scaf_pos = 1
		sum_depth = 0
		last_scaf = None
		for line in inFl:

			ct += 1
			scaf, pos, depth = line.strip().split()
			if last_scaf == None:
				last_scaf = scaf

			# End of bin on 1 scaf
			if ct == binsize:
				avg_depth = sum_depth/binsize
				print('{0}\t{1}\t{2}\t{3:.4f}'.format(last_scaf, scaf_pos-binsize, scaf_pos-1, avg_depth))
				ct = 0
				avg_depth = 0
				sum_depth = 0


			# End of scaf
			if scaf != last_scaf:
				avg_depth = sum_depth/((scaf_pos)-(scaf_pos-ct-1))
				print('{0}\t{1}\t{2}\t{3:.4f}'.format(last_scaf, scaf_pos-ct, scaf_pos, avg_depth))
				last_scaf = scaf
				scaf_pos = 0
				avg_depth = 0
				ct = 0
				sum_depth = 0
			scaf_pos += 1
			depth = int(depth)
			sum_depth += depth

		# Last scaf in file
		avg_depth = sum_depth/((scaf_pos-1)-(scaf_pos-1-ct-1))
		print('{0}\t{1}\t{2}\t{3:.4f}'.format(last_scaf, scaf_pos-1-ct-1, scaf_pos-1, avg_depth))
