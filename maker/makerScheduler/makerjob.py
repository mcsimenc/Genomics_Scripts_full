#!/usr/bin/env python3

class MakerJob:

	def __init__(self, master_log):

		import os.path

		self.master_log = master_log

		# Create master logfile is it doesn't exist
		if not os.path.isfile(master_log):
			open(master_log, 'w')

		# Determine run unique id to be the last run's id + 1
		with open(master_log, 'r') as master_log_read:
			for line in master_log_read:
				pass
			try:
				id = int(line.split('\t')[0]) + 1

			except NameError:
				id = 1

		# Write run unique id to master logfile
		with open(master_log, 'a') as master_log_append:
			master_log_append.write(str(id))


	def help():
		print('''
			Usage:
			------------
			python3 makerjob.py [opts]

			Description:
			------------
			Submits MAKER jobs and outputs logfiles and statistics.
			The default master logfile resides at:
			/share/apps/scratch/derlab/azolla/annotation/MAKER_LOG

			Options:
			------------
			-help  Output this help.

			-log [logfile]  Specify alternative master logfile.
			

			''')
		sys.exit(0)


class MakerScheduler:

	def __init__(self):

		import sys

		args = sys.argv

		# Parse -log option
		if '-log' in args:
			self.log = args[args.index('-log') + 1]
		# Sets default master logfile
		else:
			#-# ADD CODE THAT CONFIRMS USER WANTS TO USE THIS LOGFILE
			self.log = '/share/apps/scratch/derlab/data/azolla/annotations/nucl/MASTER_LOG'

		#-# ADD CODE THAT PARSES -schedule OPTION
		#-# ADD CODE THAT PARSES SETTINGS FROM ARGV, if -schedule is not specified

	def makerjob(self, master_log, settings):

		# Instantiation writes id to first field of next line in logfile
		job = MakerJob(master_log)

		#-# ADD CODE CALLING OTHER METHODS FOR RUNNING JOB



test = MakerScheduler()
test.makerjob(test.log,None)
