#!/usr/bin/env python3

import sys



def help():
	print('''
		Usage:
		------------
		GetPlantTribesOGinfo.py < inputfile [options] > outputfile

		Description:
		------------
		Retrieves orthogroup annotation information from PlantTribes classifications.

		Output:
		------------
		Default output is the entire line from the PlantTribes annotation file for that orthogroup
		and two additional columns with PlantTribes gene names and, if -q is specified, additional
		sequences if they were present in the second column of the input file that mapped to that
		orthogroup, respectively.

		Options:
		------------
		-a	Path to orthogroup annotation file. MANDATORY. Defaults to:
				/home/joshd/data/other/PlantTribes/22Gv1.1/annot/orthomcl.avg_evalue.summary
			Other possibilities are:
				/home/joshd/data/other/PlantTribes/22Gv1.1/annot/orthofinder.avg_evalue.summary
				/home/joshd/data/other/PlantTribes/22Gv1.1/annot/gfam.avg_evalue.summary

		-l	Path to gene-orthogroup mapping file MANDATORY. Defaults to:
				/home/joshd/data/other/PlantTribes/22Gv1.1/annot/orthomcl.list
			Other possibilities are:
				/home/joshd/data/other/PlantTribes/22Gv1.1/annot/orthofinder.list
				/home/joshd/data/other/PlantTribes/22Gv1.1/annot/gfam.list


		inputfile   A list of sequence names corresponding to genes in PlantTribes clusters
			    if mapping from gene names to OGs. A two-column tab-delimited file may
			    used where PlantTribes gene names are in the first column and some other
			    information is in the second column that is treated as being paired with
			    the PlantTribes gene, so the other information is mapped to an orthogroup
			    and output. This script was written for putative functional annotation
			    of plant genes from BLAST results, and the second column was orignially
			    meant to contain an unknown sequence that had high similarity with the
			    PlantTribes gene in the first column.
		    -OR-
			    A list of orthogroup IDs if mapping from OGs to PlantTribes gene names

		-go	    map gene names to OG IDs (incompatible with -og)
		-og	    map OG IDs to gene names (incompatible with -go)

		-jg	Just genes. Output a list of gene names (compatible with -og. overrides -s)

		-q	Use with -go. Outputs query names (whatever is in the second column of the input file)
			and counts for each OG.

		-s	Print short output (OG ID, number of genes, genes)
			if -q is specified: (OG ID, number of genes, genes, number of other sequences, other sequences)

		''')
	sys.exit(0)


args = sys.argv

if '-h' in args or '-help' in args or len(args)<2:
	help()
if '-go' in args and '-og' in args:
	help()

s = False
if '-s' in args:
	s = True


try:
	a = args[args.index('-a')+1]
except (IndexError, ValueError):
	a = '/home/joshd/data/other/PlantTribes/22Gv1.1/annot/orthomcl.avg_evalue.summary'

try:
	l = args[args.index('-l')+1]
except (IndexError, ValueError):
	l = '/home/joshd/data/other/PlantTribes/22Gv1.1/annot/orthomcl.list'





# Parse OG-gene mapping
OGmap = {}
for line in open(l):
	contents = line.strip().split()
	OG = int(contents[0])
	geneName = contents[1]

	try:
		OGmap[OG].add(geneName)
	except KeyError:
		OGmap[OG] = set([geneName])

# Parse OG description
OGannot = {}
header = None
for line in open(a):
	if line.startswith('O'):
		header = line.strip()
	else:
		contents = line.strip().split('\t')
		OG = int(contents[0])
		OGannot[OG] = '\t'.join(contents[1:])



# Map gene names to OG
if '-go' in args:

	# Map gene names to OG and keep associated query (For blast(nx) against PT DB
	if '-q' in args:
		# Put gene names in a dictionary as keys with values of query names in a list
		seqDict = {}
		for line in sys.stdin:
			contents = line.strip().split('\t')
			gene = contents[0]
			query = contents[1]
			try:
				seqDict[gene].append(query)
			except KeyError:
				seqDict[gene] = [query]

		# Map seqs  to OGs
		seqOGmap = {}
		for seqName in seqDict.keys():
			for OG in OGmap:
				if seqName in OGmap[OG]:

					try:
						seqOGmap[OG][0].add(seqName)
						seqOGmap[OG][1] = seqOGmap[OG][1].union([query for query in seqDict[seqName]])
					except KeyError:
						seqOGmap[OG] = [ set([seqName]), set([query for query in seqDict[seqName]]) ]

		# Output
		if '-s' not in args:
			print('{0}\tCount\tGenes\tNumQueries\tQueries\r'.format(header))
			for OG in sorted(list(seqOGmap.keys())):
				print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\r'.format(OG,OGannot[OG],str(len(seqOGmap[OG][0])),';'.join(seqOGmap[OG][0]), str(len(seqOGmap[OG][1])), ';'.join(list(seqOGmap[OG][1]))))

		else:
			print('OG_ID\tCount\tGenes\tNumQueries\tQueries\r')
			for OG in sorted(list(seqOGmap.keys())):
				print('{0}\t{1}\t{2}\t{3}\t{4}\r'.format(OG,str(len(seqOGmap[OG][0])),';'.join(seqOGmap[OG][0]), str(len(seqOGmap[OG][1])), ';'.join(list(seqOGmap[OG][1]))))
		

	# Map just gene names to OG
	else:
		# Put all the gene names in the inputfile into seqSet
		seqSet = set()
		for line in sys.stdin:
			seqSet.add(line.strip())

		# Map seqs from inputfile seqlist
		seqOGmap = {}
		for seqName in seqSet:
			for OG in OGmap:
				if seqName in OGmap[OG]:

					try:
						seqOGmap[OG].add(seqName)
					except KeyError:
						seqOGmap[OG] = set([seqName])
		# Output
		if '-s' not in args:
			print('{0}\tCount\tGenes\r'.format(header))
			for OG in sorted(list(seqOGmap.keys())):
				print('{0}\t{1}\t{2}\t{3}\r'.format(OG,OGannot[OG],str(len(seqOGmap[OG])),';'.join(seqOGmap[OG])))

		else:
			print('OG_ID\tCount\tGenes\r')
			for OG in sorted(list(seqOGmap.keys())):
				print('{0}\t{1}\t{2}\r'.format(OG,str(len(seqOGmap[OG])),';'.join(seqOGmap[OG])))

if '-og' in args:
	OGseqs = set()
	for line in sys.stdin:
		try:
			OGseqs.add(int(line.strip()))
		except ValueError:
			continue

	# Output
	if '-jg' in args:
		for OG in OGseqs:
			for gene in OGmap[OG]:
				print(gene)
			
	elif s == False:
		print('{0}\tCount\tGenes\r'.format(header))
		for OG in sorted(list(OGseqs)):
			print('{0}\t{1}\t{2}\t{3}\r'.format(OG,OGannot[OG],str(len(OGmap[OG])),','.join(OGmap[OG])))

	elif s == True:
		print('OG_ID\tCount\tGenes\r')
		for OG in sorted(list(OGseqs)):
			print('{0}\t{1}\t{2}\r'.format(OG,str(len(OGmap[OG])),','.join(OGmap[OG])))
