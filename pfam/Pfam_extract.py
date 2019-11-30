#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		Pfam_extract.py -f <file> -type <hmm or full> [options]

		Description:
		------------
		Extracts information from Pfam database and prints hmms to stdout
		or to individual files is -hmmout is used.
		

		Options:
		------------
		-f		Input file.
		
		-type		Input type: hmm or full

		-hmmout	<opt>	If extracting HMMs and this option is used,
				write each HMM to a separate file using <opt>
				as the prefix where <opt> is either acc or
				id such that files are named <opt>.hmm
				e.g. if <opt> is acc files will be named
				like PF00026.21.hmm, or if <opt> is id, files
				will be named like Asp.hmm

		-pat		Comma-separated list of patterns to search
				for in file.

		-patfl		File with list of patterns to search
				for in file.

		-nopat		Comma-separated list of patterns to search
				for in file. Matching entries are not returned
				even if other parts match patterns from pat.
				
		-nopatfl	File with list of patterns to search
				for in file. Matching entries are not returned
				even if other parts match patterns from pat.

		-acc		Comma-separated list of accessions to search
				for in file.

		-accfl		File with list of accessions to search
				for.

		-i		Case-insensitive matching for patterns in pat
				or patfl.

		''')
	sys.exit(0)


args = sys.argv


if "-help" in args or "-h" in args or len(args) < 5 or '-f' not in args or '-type' not in args:
	help()


inflname = args[args.index('-f') + 1]
fltype = args[args.index('-type') + 1]

if fltype == 'hmm' or fltype == 'full':
	pass
else:
	help()

if '-acc' in args:
	accs = args[args.index('-acc') + 1].split(',')
else:
	accs = []

if '-pat' in args:
	pats = args[args.index('-pat') + 1].split(',')
else:
	pats = []

if '-nopat' in args:
	nopats = args[args.index('-nopat') + 1].split(',')
else:
	nopats = []

if '-accfl' in args:
	accflname = args[args.index('-accfl') + 1]
	with open(accflname) as accfl:
		accs += accfl.read().split('\n')

if '-patfl' in args:
	patflname = args[args.index('-patfl') + 1]
	with open(patflname) as patfl:
		pats += patfl.read().split('\n')
if '' in pats:
		pats.pop(pats.index(''))

if '-nopatfl' in args:
	nopatflname = args[args.index('-nopatfl') + 1]
	with open(nopatflname) as nopatfl:
		nopats += nopatfl.read().split('\n')
if '' in nopats:
		nopats.pop(nopats.index(''))


if '-hmmout' in args:
	opt = args[args.index('-hmmout') +1 ]

info = []
match = 0
nopatmatch = 0
collect = 0
with open(inflname) as infl:

	for line in infl:

		if fltype == 'full':

			if line.startswith('# STOCKHOLM'):
				collect = 1
				nopatmatch = 0
			elif line.startswith('#=GF SQ'):
				collect = 0
				if match == 1 and nopatmatch == 0:
					for l in info:
						print(l, end = '')
						match = 0
					print('\n')

				info = []
	
			elif line.startswith('#=GF AC'):
				if '-acc' in args or '-accfl' in args:
					for acc in accs:
						if accs in line:
							match = 1

			if collect == 1 and nopatmatch == 0:
				info.append(line)

				if '-pat' in args or '-patfl' in args:
					if not line.startswith('#=GF RA') and not line.startswith('#=GF RL'):
						for pat in pats:
							if '-i' in args:
								if pat.lower() in line.lower():
									match = 1
							else:
								if pat in line:
									match = 1
				if '-nopat' in args or '-nopatfl' in args:
					if not line.startswith('#=GF RA') and not line.startswith('#=GF RL'):
						for nopat in nopats:
							if '-i' in args:
								if nopat.lower() in line.lower():
									nopatmatch = 1
							else:
								if nopat in line:
									nopatmatch = 1


		elif fltype == 'hmm':

			if line.startswith('HMMER3'):
				info = [line]
				match = 0

			elif line.startswith('ACC') and accs != []:

				if line.strip().split()[1] in accs:
					match = 1
					info.append(line)
				else:
					match = -1

			elif line.startswith('DESC') and pats != []:

				MATCH = False

				for pat in pats:

					if '-i' in args:

						if pat.lower() in line.lower():

							match = 1
							info.append(line)
							MATCH = True
							break

						else:
							match = -1
					else:

						if pat in line:

							match = 1
							info.append(line)
							MATCH = True
							break

						else:
							match = -1

				if MATCH == True:

					for pat in nopats:

						if '-i' in args:

							if pat.lower() in line.lower():

								match = -1
								break

							else:
								match = 1
						else:

							if pat in line:

								match = -1
								break

							else:
								match = 1


			elif match == -1:

				continue

			elif line.startswith('//'):
				info.append(line)
				if '-hmmout' in args:
					opt = args[args.index('-hmmout') +1 ]
					if opt == 'acc':
						with open('{0}.hmm'.format(info[2].split()[1]), 'w') as hmmoutfl:
							for l in info:
								hmmoutfl.write(l)
					elif opt == 'id':
						with open('{0}.hmm'.format(info[1].split()[1]), 'w') as hmmoutfl:
							for l in info:
								hmmoutfl.write(l)
					else:
						print('When using -hmmout you need to specify either: -hmmout acc OR -hmmout id', file=sys.stderr)
						sys.exit(0)
				else:
					for l in info:
						print(l, end='')

			else:
				info.append(line)
