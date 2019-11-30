#!/usr/bin/env python3

import sys

def help():
	print('''
		Usage:
		------------
		retrotransposonNamesFromDomainOrganization.py -features <file> -domains <file>
		-OR-
		retrotransposonNamesFromDomainOrganization.py -features <file -names <file>

		Description:
		------------
		Takes a two column file as input via -features and a list of comma-separated
		protein domains via -domains and outputs feature names (from the first column
		of the -features file) if the domain organization of the feature is one of those
		in the -domains file.



		Options:
		------------
		-features	A two-column tab-separated file. It's assumed that the first column
				is the name of a feature and the second column is a component of that
				feature and that components for a given feature are in order such that
				a compenent at row n is before the component at row n+1

		-domains	Lines in this file should be comma separated names of domains.

		-names		Print out domain structure as comma-separated list for feature names in
				the file specified by -names.
		
		''')
	sys.exit(0)


args = sys.argv

if len(args) != 5 or '-features' not in args:
	help()

features_fl_pth =  args[args.index('-features') + 1]

if '-domains' in args:
	domains_fl_pth =  args[args.index('-domains') + 1]
elif '-names' in args:
	names_fl_pth =  args[args.index('-names') + 1]


d = {} # this dict will have domain organization for each ltr in the -features file


with open(features_fl_pth) as features_fl:
	for line in features_fl:
		contents = line.split()
		ltrname = contents[0]
		domain = contents[1]
		if ltrname in d:
			d[ltrname].append(domain)
		else:
			d[ltrname] = [domain]
if '-domains' in args:
	domain_organization = []
	with open(domains_fl_pth) as domains_fl:
		for line in domains_fl:
			domain_organization.append(line.strip().split(','))

	for ltr in d:
		if d[ltr] in domain_organization:
			print(ltr)

elif '-names' in args:
	names_list = []
	with open(names_fl_pth) as names_fl:
		for line in names_fl:
			names_list.append(line.strip())

	for ltr in d:
		if ltr in names_list:
			print('{0}\t{1}'.format(ltr, ','.join(d[ltr])))
