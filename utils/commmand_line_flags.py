#!/usr/bin/env python3

import sys

class CLFlags:
	'''
	Parses and holds command line flags and their values.
	  Depends: sys.argv

	Properties:
	  args (list)
	  flags (dict)
	
		- 
	'''
	def __init__(self):
		self.args = sys.argv
		self.flags = {}

	def parse(flags=None, convert=str, num_beyond_flag=1, prefix='-')
		'''
		If type(flags)==str, parse as single arg. If type(flags)==iterable, parse all.
		'''
		if type(flags) == str:
			if not flags.startswith(prefix):
				flags = prefix+flags
			flags = [flags]

		for flag in flags:
			self.flags[flag.strip(prefix)] = args[args.index(flag)+num_beyond_flag:args.index(flag)+num_beyond_flag]
