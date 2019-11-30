#!/usr/bin/env python3

import os
import sys
import mysql.connector as mysql

def help():
	print('''
		Usage:
		------------
		makerGFF2mysql2featDistributions.py [options] 

		Description:
		------------
		Converts a GFF3 file to a tab-delimited file with
		the same information, but with each key-value pair from the
		input.gff expanded into it's own column. This 

		The format I'm using for naming tables is like Sacu_maker_005_2016_06_14

		Options:
		------------
		-gff [path]		Convert GFF3 to a tab-delimited file written
					to the directory given by -o. If -gff and -tab
					are both specified -gff will be ignored.

		-tab [path]		The path to a tab-delimited file produced by
					script using the -gff option. If -gff and -tab
					are both specified -gff will be ignored.

		-table [string]		The name to be given to the MySQL table created
					from the file provided using -tab or gff, one
					of which must be specified when using -table.

		-mysqldb [string]	The name of the MySQL database to use.

		-o [path]		File will be written to this directory. Defaults
					to the directory this script is run from.

		-prefix [string]	Prefix for output files. Defaults to input file
					name.

		-stats			Get stats for table specified by -table.

		''')
	sys.exit(0)



def gff2tab(infl, outfl):
	'''
	The entire file is stored in memory. The attributes column is expanded to tab delimited format
	and printed in a sorted order. Richard Leyba developed this function Spring 2016.
	'''

	print("Converting GFF3 file {0} to tab-delimited file {1} for MySQL: ".format(infl.name, outfl.name), end='')

	try:
		attributes = set()
		gffdict = {}
		linenum = 0

		# Add QI attributes
		attributes.add('5_utr_length')
		attributes.add('fraction_splice_sites_confirmed_by_est')
		attributes.add('fraction_exons_overlapping_est')
		attributes.add('fraction_exons_overlapping_est_or_protein')
		attributes.add('fraction_splice_sites_confirmed_by_snap')
		attributes.add('fraction_exons_overlapping_snap_pred')
		attributes.add('number_of_exons_in_mrna')
		attributes.add('3_utr_length')
		attributes.add('mrna_protein_length')

		for line in infl:

			if line.startswith('#'):
				continue

			contents = line.strip().split('\t')
			linenum += 1

			try:
				col9list = contents[8].split(';')
			except IndexError: # some lines may not be GFF3 standard. Print such lines to stderr
				print(line, file=sys.stderr)
				continue

			# split the key-value attributes
			gffdict[linenum] = {}
			gffdict[linenum]['gff'] = contents[0:8]

			for pair in col9list:
				attribute = pair.split('=')
				AttributeKey = attribute[0].strip('_')
				if AttributeKey == 'QI':
					AttributeValue = [ i for i in attribute[1].split('|')]
					gffdict[linenum]['5_utr_length'] = AttributeValue[0]
					gffdict[linenum]['fraction_splice_sites_confirmed_by_est'] = AttributeValue[1]
					gffdict[linenum]['fraction_exons_overlapping_est'] = AttributeValue[2]
					gffdict[linenum]['fraction_exons_overlapping_est_or_protein'] = AttributeValue[3]
					gffdict[linenum]['fraction_splice_sites_confirmed_by_snap'] = AttributeValue[4]
					gffdict[linenum]['fraction_exons_overlapping_snap_pred'] = AttributeValue[5]
					gffdict[linenum]['number_of_exons_in_mrna'] = AttributeValue[6]
					gffdict[linenum]['3_utr_length'] = AttributeValue[7]
					gffdict[linenum]['mrna_protein_length'] = AttributeValue[8]

				else:
					AttributeValue = attribute[1]
					attributes.add(AttributeKey)
					gffdict[linenum][AttributeKey] = AttributeValue

		# Convert attribute set to list for looping through to print attributes out in order
		attrList = sorted(list(attributes))

		# Print headers for columns 1-8
		#print('seqid\tsource\ttype\tstart\tend\tscore\tstrand\tphase', end='')
		outfl.write('seqid\tsource\ttype\tstart\tend\tscore\tstrand\tphase')

		# Print headers for attributes column
		for attr in attrList:
			outfl.write('\t{0}'.format(attr))
			#print('\t', end='')
			#print(attr, end='')
		#print('\n', end='')
		outfl.write('\n')

		# Print data
		for i in range(1, len(gffdict)+1):
			# Print columns 1-8
			#print('\t'.join(gffdict[i]['gff']), end='')
			outfl.write('\t'.join(gffdict[i]['gff']))

			# Print attributes. If no attribute print a period
			for attr in attrList:
				#print('\t', end='')
				outfl.write('\t')
				try:
					#print(gffdict[i][attr], end='')
					outfl.write(gffdict[i][attr])
				except KeyError:
					#print('.', end='')
					outfl.write('.')

			#print('\n', end='')
			outfl.write('\n')
	except Error as err:
		print(err)

	else:
		print("done.")




def mysql_connect(mysqldb):

	# Connect to MySQL DB. Create it if it does not exist.
	print('Connecting to MySQL database {0}:'.format(mysqldb), end='')
	try:
		connection = mysql.connect(user='derstudent', password='pl@ntGen0me', database=mysqldb, host='localhost', raw=False, get_warnings=False)

	except mysql.Error as err:
		if err.errno == mysql.errorcode.ER_BAD_DB_ERROR:
			print(' does not exist. Creating database...', end='')
			connection = mysql.connect(user='derstudent', password='pl@ntGen0me', host='localhost', raw=False, get_warnings=False)
			cursor = connection.cursor()
			make_db = 'CREATE DATABASE `{0}`'.format(mysqldb)

			try:
				cursor.execute(make_db)
			except mysql.Error as err:
				print(err)
				sys.exit(1)
			else:
				print('database created!')
				connection.database = mysqldb
				
		else:
			print(err)
			sys.exit(1)
	else:
		print(' connected!')
		cursor = connection.cursor()

	return connection,cursor


def create_mysql_table(table, cursor, connection):

	tables = {}
 
	# Set data types for columns in table
	tables[table] = (
		"CREATE TABLE `{0}` ("
		" `seqid` VARCHAR(100),"
		" `source` VARCHAR(100),"
		" `type` VARCHAR(100),"
		" `start` INT(15),"
		" `end` INT(15),"
		" `score` DOUBLE(7,5),"
		" `strand` SET('.','-','+'),"
		" `phase` SET('.','0','1','2'),"
		" `3_utr_length` INT(7),"
		" `5_utr_length` INT(7),"
		" `AED` DOUBLE(5,3),"
		" `Gap` VARCHAR(1000),"
		" `ID` VARCHAR(1000),"
		" `Name` VARCHAR(1000),"
		" `Parent` VARCHAR(1000),"
		" `Target` VARCHAR(1000),"
		" `eAED` DOUBLE(5,3),"
		" `fraction_exons_overlapping_est` DOUBLE(6,4),"
		" `fraction_exons_overlapping_est_or_protein` DOUBLE(6,4),"
		" `fraction_exons_overlapping_snap_pred` DOUBLE(6,4),"
		" `fraction_splice_sites_confirmed_by_est` DOUBLE(6,4),"
		" `fraction_splice_sites_confirmed_by_snap` DOUBLE(6,4),"
		" `mrna_protein_length` INT(7),"
		" `number_of_exons_in_mrna` INT(5)"
		")"
		).format(table)

	# Create tables
	for name, ddl in tables.items():
		print("Creating table {0}: ".format(name), end='')
		try:
			cursor.execute(ddl)
		except mysql.Error as err:
			if err.errno == mysql.errorcode.ER_TABLE_EXISTS_ERROR:
				print("table exists.")
			else:
				print(err)
				sys.exit(2)

		else:
			connection.commit()
			print("table created successfully.")


def load_mysql_data(infl, table, cursor, connection):

	# Load data into table. Ignore the first line because it's a header. Set all periods to NULL
	load_data_query = ("LOAD DATA LOCAL INFILE '{0}' INTO TABLE `{1}` IGNORE 1 LINES"
			" (@vseqid,@vsource,@vtype,@vstart,@vend,@vscore,@vstrand,@vphase,@v3_utr_length,"
			" @v5_utr_length,@vAED,@vGap,@vID,@vName,@vParent,@vTarget,@veAED,"
			" @vfraction_exons_overlapping_est,@vfraction_exons_overlapping_est_or_protein,"
			" @vfraction_exons_overlapping_snap_pred,@vfraction_splice_sites_confirmed_by_est,"
			" @vfraction_splice_sites_confirmed_by_snap,@vmrna_protein_length,@vnumber_of_exons_in_mrna)"
			" SET"
			" seqid = nullif(@vseqid,'.'),"
			" source = nullif(@vsource,'.'),"
			" type = nullif(@vtype,'.'),"
			" start = nullif(@vstart,'.'),"
			" end = nullif(@vend,'.'),"
			" score = nullif(@vscore,'.'),"
			" strand = nullif(@vstrand,'.'),"
			" phase = nullif(@vphase,'.'),"
			" 3_utr_length = nullif(@v3_utr_length,'.'),"
			" 5_utr_length = nullif(@v5_utr_length,'.'),"
			" AED = nullif(@vAED,'.'),"
			" Gap = nullif(@vGap,'.'),"
			" ID = nullif(@vID,'.'),"
			" Name = nullif(@vName,'.'),"
			" Parent = nullif(@vParent,'.'),"
			" Target = nullif(@vTarget,'.'),"
			" eAED = nullif(@veAED,'.'),"
			" fraction_exons_overlapping_est = nullif(@vfraction_exons_overlapping_est,'.'),"
			" fraction_exons_overlapping_est_or_protein = nullif(@vfraction_exons_overlapping_est_or_protein,'.'),"
			" fraction_exons_overlapping_snap_pred = nullif(@vfraction_exons_overlapping_snap_pred,'.'),"
			" fraction_splice_sites_confirmed_by_est = nullif(@vfraction_splice_sites_confirmed_by_est,'.'),"
			" fraction_splice_sites_confirmed_by_snap = nullif(@vfraction_splice_sites_confirmed_by_snap,'.'),"
			" mrna_protein_length = nullif(@vmrna_protein_length,'.'),"
			" number_of_exons_in_mrna = nullif(@vnumber_of_exons_in_mrna,'.')"
			).format(infl, table)

	print("Loading {0} into table {1}: ".format(infl, table), end='')
	try:
		cursor.execute(load_data_query)
	except mysql.Error as err:
		print(err)
	else:
		connection.commit()
		print("loaded successfully.")




def getstatsMySQL(table, outdir, prefix, cursor, connection):

	connection = mysql.connect(user='derstudent', password='pl@ntGen0me', database=mysqldb, host='localhost', raw=False, get_warnings=False)
	cursor = connection.cursor()


	# Queries
	queries = {}
	queries['source counts'] = ("SELECT `source`, count(*) FROM `{0}`"
				" GROUP BY `source` INTO OUTFILE '{1}/{2}.sources'"
				).format(table, outdir, prefix)

	queries['type counts'] = ("SELECT `type`, count(*) FROM `{0}` GROUP BY `type`"
				" INTO OUTFILE '{1}/{2}.types'"
				).format(table, outdir, prefix)

	#queries['AED distribution'] = ("SELECT `AED`, count(*), `type` FROM `{0}` GROUP BY `AED`"
	#			" INTO OUTFILE '{1}/{2}.AED'"
	#			).format(table, outdir, prefix)

	#queries['eAED distribution'] = ("SELECT `eAED`, count(*), `type` FROM `{0}` GROUP BY `eAED`"
	#			" INTO OUTFILE '{1}/{2}.eAED'"
	#			).format(table, outdir, prefix)


	cursor.execute(queries['source counts'])
	cursor.execute(queries['type counts'])

	# Get AED and eAED distributions for each type of feature
	with open('{0}/{1}.types'.format(outdir, prefix)) as typesfl:

		AED_features = ['mRNA']
		length_features = ['CDS', 'gene', 'mRNA', 'exon']
		mRNA_features = ['fraction_exons_overlapping_est','fraction_exons_overlapping_est_or_protein','fraction_exons_overlapping_snap_pred','fraction_splice_sites_confirmed_by_est','fraction_splice_sites_confirmed_by_snap','mrna_protein_length','number_of_exons_in_mrna']

		for line in typesfl:

			type = line.split('\t')[0]


		#	AED_query = ("SELECT `AED`, count(*) FROM `{0}` WHERE type='{3}' GROUP BY `AED`"
		#		" INTO OUTFILE '{1}/{2}.{3}_AED'"
		#		).format(table, outdir, prefix, type)

			AED_query = ("SELECT `ID`,`AED` FROM `{0}` WHERE type='{3}'"
				" INTO OUTFILE '{1}/{2}.{3}.AED'"
				).format(table, outdir, prefix, type)
			
		#	eAED_query = ("SELECT `eAED`, count(*) FROM `{0}` WHERE type='{3}' GROUP BY `eAED`"
		#		" INTO OUTFILE '{1}/{2}.{3}_eAED'"
		#		).format(table, outdir, prefix, type)

			eAED_query = ("SELECT `ID`,`eAED` FROM `{0}` WHERE type='{3}'"
				" INTO OUTFILE '{1}/{2}.{3}.eAED'"
				).format(table, outdir, prefix, type)

		#	length_query = ("SELECT `end`-`start`+1 as `length`, count(*) from `{0}` WHERE type='{3}'"
		#		" GROUP BY `length` INTO OUTFILE '{1}/{2}.{3}_lengths'"
		#		).format(table, outdir, prefix, type)

			length_query = ("SELECT `ID`,`end`-`start`+1 as `length` from `{0}` WHERE type='{3}'"
				" INTO OUTFILE '{1}/{2}.{3}.lengths'"
				).format(table, outdir, prefix, type)

			if type in AED_features:
				cursor.execute(AED_query)
				cursor.execute(eAED_query)

			if type in length_features:
				cursor.execute(length_query)

		for feature in mRNA_features:

			query = ("SELECT `ID`, `{3}` from `{0}` WHERE type='mRNA'"
				" INTO OUTFILE '{1}/{2}.mRNA.{3}'"
				).format(table, outdir, prefix, feature)

			cursor.execute(query)

	#for name, query in queries.items():

	#	print("Getting {0}: ".format(name), end='')
	#	try:
	#		if name == 'type counts':
	#			
	#		cursor.execute(query)
	#	except mysql.Error as err:
	#		print("file may already exist.")
	#	else:
	#		print("done.")
	




args = sys.argv

# Display help if:
if len(args) == 1:
	help()

if '-table' in args:
	if '-mysqldb' not in args:
		print("Specify a MySQL database using -mysqldb")
		sys.exit(0)

elif '-gff' not in args and '-tab' not in args:
	print("Specify an input file using -tab of -gff")
	sys.exit(0)

# Get output directory
try:
	outdir = args[args.index('-o') + 1]
	if not outdir.startswith('/'):
		outdir = '{0}/{1}'.format(os.getcwd(), outdir)
except:
	outdir = os.getcwd()
	
if '-prefix' in args:
	prefix = args[args.index('-prefix') + 1]


# Convert GFF3 to tab-delimited
if '-gff' in args and '-tab' not in args:
	infl = args[args.index('-gff') + 1]

	try:
		prefix
	except:
		prefix = infl.split('/')[-1]

	try:
		gff3 = open(infl)
	except FileNotFoundError:
		print("File specified by -gff doesn't exist.")
		sys.exit(1)
	else:
		tab = open("{0}/{1}.tab".format(outdir, prefix), 'w')
		gff2tab(gff3,tab)
		gff3.close()

	# For using with -mysql option
	infl = "{0}/{1}.tab".format(outdir, prefix)

elif '-tab' in args:
	infl = args[args.index('-tab') + 1]

	try:
		tab = open(infl)
	except FileNotFoundError:
		print("File specified by -tab doesn't exist.")
		sys.exit(1)
	else:
		tab.close()




if '-table' in args:

	table = args[args.index('-table') + 1]
	mysqldb = args[args.index('-mysqldb') + 1]

	mysql_connection_and_cursor = mysql_connect(mysqldb)
	connection = mysql_connection_and_cursor[0]
	cursor = mysql_connection_and_cursor[1]

	create_mysql_table(table, cursor, connection)
	if '-gff' in args or '-tab' in args:
		load_mysql_data(infl, table, cursor, connection)

	if '-stats' in args:
		getstatsMySQL(table, outdir, prefix, cursor, connection)


	# Close connection
	cursor.close()
	connection.close()
