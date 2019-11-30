#!/usr/bin/env python3

import os
import sys
import re
import time
import subprocess
import copy

class MakerJob:

	'''
	Methods:
	__init__
	select_dir
	qsubmit
	make_ctl
	generate_stats
	make_snap_hmm
	'''

	def __init__(self, master_log, base_output_dir, schd_fl_pth, opt_dct):

		'''
		Initializes object with data attribute self.master_log holding path to the
		master logfile and writes a unique id to this job's row in that file. Creates
		new logfile if it does not exist, though the directory to contain the logfile
		must exist.
		'''

		# Keep the master log path and the dict with this run's options as attributes
		self.master_log = master_log
		self.opt_dct = opt_dct

		# Save this run's output path as an attribute, self.output_dir
		#if base_output_dir.endswith('/'):
		#	self.output_dir = base_output_dir + opt_dct['name']
		#else:
		#	self.output_dir = base_output_dir + '/' + opt_dct['name'] + '/'
		self.output_dir = base_output_dir + opt_dct['name'] + '/'

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

		# Write  to log file
		with open(master_log, 'a') as master_log_append:
			master_log_append.write('\n' + str(id) + '\t' + opt_dct['name'] + '\t' + schd_fl_pth + '\t' + self.output_dir)

		# Create output dir
		self.select_dir(base_output_dir)
		self.select_dir(self.output_dir)


	def select_dir(self, path):

		'''
		Make directory for maker job ctl, qsub, and output files if the directory
		does not exist.
		'''

		try:
			os.chdir(path)

		except OSError:
			os.mkdir(path)


	def qsubmit(self, joblist):

		'''
		Create and submit qsub file. Write options to logfiles.
		'''

		resources_opt = 'nodes=' + self.opt_dct['qsub']['nodes'] + ':ppn=' +  self.opt_dct['qsub']['ppn']
		total_cpu = str(int(self.opt_dct['qsub']['nodes']) * int(self.opt_dct['qsub']['ppn']))

		with open(self.output_dir + '/' + self.opt_dct['name'] + '.qsub', 'w') as qsub_script_fl:
			qsub_script_fl.write('#!/bin/bash\n')
			qsub_script_fl.write('#PBS -k ' + self.opt_dct['qsub']['k'] + '\n')
			qsub_script_fl.write('#PBS -N ' + self.opt_dct['name'] + '\n')
			qsub_script_fl.write('#PBS -q ' + self.opt_dct['qsub']['q'] + '\n')
			qsub_script_fl.write('#PBS -j ' + self.opt_dct['qsub']['j'] + '\n')
			qsub_script_fl.write('#PBS -m ' + self.opt_dct['qsub']['m'] + '\n')
			qsub_script_fl.write('#PBS -M ' + self.opt_dct['qsub']['M'] + '\n')
			qsub_script_fl.write('#PBS -l ' + resources_opt + '\n')
			qsub_script_fl.write('module load genomics/all\n')
			qsub_script_fl.write('export LD_PRELOAD=/share/apps/openmpi-1.8.7/lib/libmpi.so\n')
			qsub_script_fl.write('cd ' + self.output_dir + '\n')
			qsub_script_fl.write('echo "START"\n')
			qsub_script_fl.write('date\n')
			qsub_script_fl.write('mpiexec -n ' + total_cpu + ' maker ' + self.output_dir + '/maker_bopts.ctl ' + self.output_dir + '/maker_exe.ctl ' + self.output_dir + '/maker_opts.ctl 1>' + self.output_dir + '/maker.err 2>' + self.output_dir + '/maker.log\n')
			qsub_script_fl.write('echo "END"\n')
			qsub_script_fl.write('date\n')

		with open(self.master_log, 'a') as master_log_fl:
			master_log_fl.write('\t#PBS -k ' + self.opt_dct['qsub']['k'])
			master_log_fl.write('\t#PBS -N ' + self.opt_dct['name'])
			master_log_fl.write('\t#PBS -q ' + self.opt_dct['qsub']['q'])
			master_log_fl.write('\t#PBS -j ' + self.opt_dct['qsub']['j'])
			master_log_fl.write('\t#PBS -m ' + self.opt_dct['qsub']['m'])
			master_log_fl.write('\t#PBS -M ' + self.opt_dct['qsub']['M'])
			master_log_fl.write('\t#PBS -l ' + resources_opt)

		# Submits job and saves stdout. Only one job runs at once; others remain on hold until the previous one finishes.
		#if joblist == []:
		#qsub_stdout = subprocess.check_output(['qsub', self.output_dir + '/' + self.opt_dct['name'] + '.qsub'])
		qsub_stdout = subprocess.check_output('qsub {0}{1}.qsub'.format(self.output_dir, self.opt_dct['name']), shell=True)
		self.job_num = str(qsub_stdout).strip().split('.')[0][2:]
		#else:
		#	qsub_stdout = subprocess.check_output(['qsub', self.output_dir + '/' + self.opt_dct['name'] + '.qsub', '-W depend=afterok:' + ':'.join(joblist)])
		#	self.job_num = str(qsub_stdout).strip().split('.')[0][2:]

		return self.job_num

	def make_ctl(self):

		'''
		Create maker ctl files. Write options to logfiles.
		'''

		# Write options to master log
		with open(self.master_log, 'a') as master_log_fl:

			# Create maker control files
			with open(self.output_dir + '/maker_bopts.ctl', 'w') as bopts_fl:
				for opt in self.opt_dct['blast']:
					bopts_fl.write(opt + '=' + self.opt_dct['blast'][opt] + '\n')
					master_log_fl.write('\t' + opt + '=' + self.opt_dct['blast'][opt])

			with open(self.output_dir + '/maker_opts.ctl', 'w') as opts_fl:
				for opt in self.opt_dct['maker']:
					opts_fl.write(opt + '=' + self.opt_dct['maker'][opt] + '\n')
					master_log_fl.write('\t' + opt + '=' + self.opt_dct['maker'][opt])

			with open(self.output_dir + '/maker_exe.ctl', 'w') as exe_fl:
				for opt in self.opt_dct['exe']:
					exe_fl.write(opt + '=' + self.opt_dct['exe'][opt] + '\n')
					master_log_fl.write('\t' + opt + '=' + self.opt_dct['exe'][opt])


	#-# PRELIMINARY #-#
	def generate_stats(self):

		'''
		Generate statistics for maker run and write to logfiles.
		'''


		def count_gene_models(zff_pth):

			'''
			Counts unique models in zff file (named genome.ann by default by maker2zff).
			Returns number of models as integer.
			'''

			with open(zff_pth, 'r') as zff_fl:
				models = set()
				for line in zff_fl:
					if not line.startswith('>'):
						models.add(re.search('MODEL[\d]+', line))

				return len(models)


		def select_gene_models(maker2zff_opts = self.opt_dct['maker2zff']):

			'''
			Runs maker2zff to select gene models.
			'''

			#input('maker2zff -x {1} -c {2} -e {3} -o {4} {0}*all.gff'.format(self.output_dir, maker2zff_opts['x'], maker2zff_opts['c'], maker2zff_opts['e'], maker2zff_opts['o']))
			if maker2zff_opts['n'] == 1:
				#subprocess.Popen('maker2zff -n {0}*all.gff'.format(self.output_dir), cwd=self.output_dir, shell=True)
				subprocess.call('maker2zff -n {0}*all.gff'.format(self.output_dir), cwd=self.output_dir, shell=True)
			else:
				#subprocess.Popen('maker2zff -x {1} -c {2} -e {3} -o {4} {0}*all.gff'.format(self.output_dir, maker2zff_opts['x'], maker2zff_opts['c'], maker2zff_opts['e'], maker2zff_opts['o']), cwd=self.output_dir, shell=True)
				subprocess.call('maker2zff -x {1} -c {2} -e {3} -o {4} {0}*all.gff'.format(self.output_dir, maker2zff_opts['x'], maker2zff_opts['c'], maker2zff_opts['e'], maker2zff_opts['o']), cwd=self.output_dir, shell=True)


		# Merge gffs
		#subprocess.Popen('gff3_merge -d {0}*maker.output/*master_datastore_index.log'.format(self.output_dir), cwd=self.output_dir, shell=True)
		subprocess.call('gff3_merge -d {0}*maker.output/*master_datastore_index.log'.format(self.output_dir), cwd=self.output_dir, shell=True)
		print('Done merging gff3 files')
		# Make zff files (outputs are genome.ann and genome.dna)
		select_gene_models()
		#time.sleep(10)
		# Get some stats on this job's output
		job_stats_bytes = subprocess.check_output('fathom {0}genome.ann {0}genome.dna -gene-stats'.format(self.output_dir), cwd=self.output_dir, shell=True)
		#job_stats_bytes = subprocess.check_output(['fathom', '{0}genome.ann'.format(self.output_dir), '{0}genome.dna'.format(self.output_dir), '-gene-stats'])
		job_stats = job_stats_bytes.decode(encoding='utf=8')
		print(job_stats)
		# Count number of "high-confidence" gene models as determined by maker2zff parameters
		self.num_models = count_gene_models('{0}genome.ann'.format(self.output_dir))
		print(self.num_models)


	#-# PRELIMINARY #-#
	def make_snap_hmm(self):

		'''
		Generate a HMM file for use in training SNAP.
		'''

		# From the Fathom help:
		# -min-intron     Sets the warning value for minimum intron length (default 30).
		# -max-intron     (default 100000)
		# -min-exon       (default 6)
		# -max-exon       (default 50000)
		# -min-gene       (default 150)
		# -max-gene       (default 200000)
		# -min-cds        (default 150)
		# -max-cds        (default 50000)
		# -categorize     Categorizes genomic regions into those that contain errors
                # (err), warnings (wrn), alternate forms (alt), overlapping
                # genes (olp), and unique genes (uni). Typically, only the
                # unique genes are used for training and testing. The value
                # of <i> limits the intergenic sequence at the ends.
		# -export         Creates 4 files export.{ann,dna,aa,tx}. The coordinates and
		#                dna file depend on the value of <int>. The -plus option
		#                converts the sequence to plus strand.

		# Prepare genomic regions for making hmm: gene regions + n bases on either side (specified by -categorize)
		#subprocess.Popen('fathom {0}genome.ann {0}genome.dna -categorize {1}'.format(self.output_dir, self.opt_dct['snap']['categorize']), cwd=self.output_dir, shell=True)
		subprocess.call('fathom {0}genome.ann {0}genome.dna -categorize {1}'.format(self.output_dir, self.opt_dct['snap']['categorize']), cwd=self.output_dir, shell=True)
		# Create files necessary for generating hmm fil
		#subprocess.Popen('fathom {0}uni.ann {0}uni.dna -export {1} -plus'.format(self.output_dir, self.opt_dct['snap']['categorize']), cwd=self.output_dir, shell=True)
		subprocess.call('fathom {0}uni.ann {0}uni.dna -export {1} -plus'.format(self.output_dir, self.opt_dct['snap']['categorize']), cwd=self.output_dir, shell=True)
		# Create more files necessary for generating hmm file
		#subprocess.Popen('forge {0}export.ann {0}export.dna'.format(self.output_dir), cwd=self.output_dir, shell=True)
		subprocess.call('forge {0}export.ann {0}export.dna'.format(self.output_dir), cwd=self.output_dir, shell=True)
		# Generate hmm file
		#subprocess.Popen('hmm-assembler.pl {0}/genome {0} > snap_{1}.hmm'.format(self.output_dir[:-1], self.opt_dct['name']), cwd=self.output_dir, shell=True)
		subprocess.call('hmm-assembler.pl {0}/genome {0} > snap_{1}.hmm'.format(self.output_dir[:-1], self.opt_dct['name']), cwd=self.output_dir, shell=True)





class MakerSchedule:

	'''
	Methods:
	__init__
	help
	run_job
	run_sched
	parse_sched_fl
	- get_rerun_opts
	'''
	

	

	def __init__(self):

		'''
		1. Initializes object with data attributes:
		    self.args     holds command line arguments.
		    self.master_log      holds master logfile path.
		    self.schd_fl_pth holds schedule file path.

		2. Calls self.help()
		'''

		self.args = sys.argv
		self.default_schd_fl_pth = '/share/apps/scratch/derlab/scripts/mkr_default.schedule'
		# MAY WANT TO TAKE THIS OUT...I CREATED THIS ATTRIBUTE TO ALLOW HOLDING OF JOBS VIA QSUB -W UNTIL PREVIOUS JOBS FINISHED, BUT IF SCRIPT WAITS ANYWAYS IN MakerSchedule.run_job THIS ISN'T NECESSARY
		self.joblist = []

		# Parse -h and -help option.
		if '-h' in self.args or '-help' in self.args:
			self.help()

		# Parse -log option.
		if '-log' in self.args:
			self.master_log = self.args[self.args.index('-log') + 1]

		else:
			# Sets default master logfile.
			#-# ADD CODE THAT CONFIRMS USER WANTS TO USE THIS LOGFILE
			self.master_log = '/share/apps/scratch/derlab/data/azolla/annotations/nucl/MASTER_LOG'

		# Parse -schedule option.
		if '-schedule' in self.args:
			self.schd_fl_pth = self.args[self.args.index('-schedule') + 1]
		else:
			# Default schedule file
			self.schd_fl_pth = '/share/apps/scratch/derlab/scripts/mkr_default.schedule'

		#-# ADD CODE THAT PARSES SETTINGS FROM ARGV, if -schedule is not specified


	def help(self):

		'''
		Prints this script's brief help.
		'''

		print('''
			Usage:
			------------
			python3 maker_scheduler.py [opts]

			Description:
			------------
			Submits MAKER jobs and outputs logfiles and statistics.	The default master 
			logfile resides at: /share/apps/scratch/derlab/azolla/annotation/MAKER_LOG

			Options:
			------------
			-h, help  Output this help.

			-log [filepath]  Specify alternative master logfile.

			-schedule [filepath] Specify schedule file. If a schedule file is specified
			 then other command line arguments may be overwritten.
			

			''')

		sys.exit(0)


	def run_job(self, run):

		'''
		Carries out tasks needed for a single maker job.
		'''

		# Creates MakerJob object
		job = MakerJob(self.master_log, self.schd_opt_dct['dir'], self.schd_fl_pth, opt_dct=self.schd_opt_dct[run])
		# Creates control files for this run
		job.make_ctl()
		# Creates qsub script and submits job to cluster
		cur_job_num = job.qsubmit(self.joblist)
		# MAY WANT TO TAKE THIS OUT...I CREATED THIS ATTRIBUTE TO ALLOW HOLDING OF JOBS VIA QSUB -W UNTIL PREVIOUS JOBS FINISHED, BUT IF SCRIPT WAITS ANYWAYS IN MakerSchedule.run_job THIS ISN'T NECESSARY
		self.joblist.append(cur_job_num)
		print('{0} submitted to cluster.'.format(job.opt_dct['name']))
		# Checks qstat until previous job has finished
		running_jobs = [cur_job_num]
		while cur_job_num in running_jobs:
			proc = str(subprocess.check_output('qstat'))
			running_jobs = re.findall('(\d+)\.kepler', proc)
			time.sleep(5)
		# Gets stats for job once the job has finished
		job.generate_stats()
		# Generate HMM for SNAP training
		if job.opt_dct['snap']['makehmm'] == '1':
			job.make_snap_hmm()
		


	def run_sched(self):

		'''
		Carries out multiple maker runs, or a single run using command line options and defaults
		if no schedule file is specified. Parses settings from schedule file or command line into
		a dictionary self.schd_opts_dct
		'''

		default_opt_dct = self.parse_schd_fl(self.default_schd_fl_pth)
		self.schd_opt_dct = self.parse_schd_fl(self.schd_fl_pth, default_opt_dct[1])

		for run in range(1,self.schd_opt_dct['run_ct'] + 1):
			self.run_job(run)



	def parse_schd_fl(self, schd_pth, default_opt_dct={}):

		'''
		Parses schedule file. Returns dict with options for individual runs as dicts; as values of
		integer keys.
		'''

		def set_cur_opt_group(self, cur_opt_group):

			'''
			Sets all options in self.cur_opt_groups to 0 except cur_opt_group.
			'''

			for opt_group in self.cur_opt_groups:
				if opt_group == cur_opt_group:
					self.cur_opt_groups[cur_opt_group] = 1
				else:
					self.cur_opt_groups[opt_group] = 0
					

		#-# PRELIMINARY #-#
		def get_rerun_opts(self, id):

			'''
			Parses the master log for runs corresponding to id. Returns a dictionary to be
			merged with the master schedule dict (schd_opt_dct).
			'''

			# Parse opts from the run in master log corresponding to id
			with open(self.master_log) as mlog:
				for line in mlog:
					if int(line.strip().split('\t')[0]) == int(id):
						pass

						# PARSE MASTER LOG AND GET OPTIONS


		# This dict keeps options for all runs. Keys are integers from 1 to the total number of runs to be performed
		#if self.schd_opt_dct in globals() or self.schd_opt_dct in locals():
		schd_opt_dct = {}
		schd_opt_dct['schd_fl_pth'] = self.schd_fl_pth

		with open(schd_pth, 'r') as schd_fl:

			# run_ct keeps count of the number of runs to be performed, for setting up schd_opt_dct
			run_ct = 0

			# Loop through the schedule file and count the number of runs
			for line in schd_fl:

				if line.startswith('@newrun'):
					run_ct += 1

				elif line.startswith('@rerun'):
					rerun_lst = line.strip().split(',')
					self.rerun_dct.update( {id:{} for id in rerun_lst} )
					run_ct += len(rerun_lst)

			# Create a key for each run in schd_opt_dct initialized as default_opt_dct
			schd_opt_dct.update( {i:copy.deepcopy(default_opt_dct) for i in list(range(1, run_ct+1))} )
			schd_opt_dct['run_ct'] = run_ct

			# cur_run keeps track of which key in schd_dct_opts to add options to. Increments when a line reads @newrun or for runs in @rerun tags
			cur_run = 0

			# These variables will be 1 if the @[var] tag is encountered in the sched file
			self.cur_opt_groups = {'maker2zff':0, 'blast':0, 'maker':0, 'exe':0, 'qsub':0, 'snap':0}

			# Loops through the schedule file again and extract options
			schd_fl.seek(0)
			for line in schd_fl:

				if line.startswith('#') or line.strip() == '':
					continue

				elif line.startswith('@dir'):
					schd_opt_dct['dir'] = line.strip().split('=')[1]
					# Standardize output dir paths so they end with a forward slash
					if not schd_opt_dct['dir'].endswith('/'):
						schd_opt_dct['dir'] = schd_opt_dct['dir'] + '/'

				elif line.startswith('@newrun'):
					set_cur_opt_group(self, 'newrun')
					cur_run += 1

				elif line.startswith('use_run'):
					set_cur_opt_group(self, 'use_run')
					id = line.strip().split('=')[1]
					schd_opt_dct[cur_run].update(get_rerun_opts(id))

				elif line.startswith('@rerun'):
					set_cur_opt_group(self, 'rerun')
					rerun_lst = line.strip().split(',')
					for id in rerun_lst:
						cur_run += 1
						schd_opt_dct[cur_run].update(get_rerun_opts(id))

				elif line.startswith('@maker2zff'):
					set_cur_opt_group(self, 'maker2zff')
					try:
						schd_opt_dct[cur_run]['maker2zff']
					except:
						schd_opt_dct[cur_run]['maker2zff'] = {}

				elif line.startswith('@snap'):
					set_cur_opt_group(self, 'snap')
					try:
						schd_opt_dct[cur_run]['snap']
					except:
						schd_opt_dct[cur_run]['snap'] = {}

				elif line.startswith('@qsub'):
					set_cur_opt_group(self, 'qsub')
					try:
						schd_opt_dct[cur_run]['qsub']
					except:
						schd_opt_dct[cur_run]['qsub'] = {}

				elif line.startswith('@blast'):
					set_cur_opt_group(self, 'blast')
					try:
						schd_opt_dct[cur_run]['blast']
					except:
						schd_opt_dct[cur_run]['blast'] = {}

				elif line.startswith('@maker'):
					set_cur_opt_group(self, 'maker')
					try:
						schd_opt_dct[cur_run]['maker']
					except:
						schd_opt_dct[cur_run]['maker'] = {}

				elif line.startswith('@exe'):
					set_cur_opt_group(self, 'exe')
					try:
						schd_opt_dct[cur_run]['exe']
					except:
						schd_opt_dct[cur_run]['exe'] = {}

				elif self.cur_opt_groups['maker2zff'] == 1:
					opt = line.strip().split('=')
					if len(opt) == 1:
						schd_opt_dct[cur_run]['maker2zff'][opt[0]] = ''
					else:
						schd_opt_dct[cur_run]['maker2zff'][opt[0]] = opt[1]
					
				elif self.cur_opt_groups['snap'] == 1:
					opt = line.strip().split('=')
					if len(opt) == 1:
						schd_opt_dct[cur_run]['snap'][opt[0]] = ''
					else:
						schd_opt_dct[cur_run]['snap'][opt[0]] = opt[1]
					# May want a try/catch here for non-ints used in this option
					# Record that the user wants to use the hmm file output from another run specified by this
					# schedule file, setting the @maker setting snaphmm to that file's path after processing all other schedule options.
					#if opt[0] == 'usehmm' and int(opt[1]) > 0:
					#	schd_opt_dct[cur_run]['snap']['prev_run_hmm'] = 1
					#	schd_opt_dct[cur_run]['snap']['prev_run_hmm_pth'] = opt[1]
					#elif opt[0] == 'usehmm' and int(opt[1]) == 0:
					#	schd_opt_dct[cur_run]['snap']['prev_run_hmm'] = 0
					
				elif self.cur_opt_groups['blast'] == 1:
					opt = line.strip().split('=')
					if len(opt) == 1:
						schd_opt_dct[cur_run]['blast'][opt[0]] = ''
					else:
						schd_opt_dct[cur_run]['blast'][opt[0]] = opt[1]
					
				elif self.cur_opt_groups['maker'] == 1:
					opt = line.strip().split('=')
					if len(opt) == 1:
						schd_opt_dct[cur_run]['maker'][opt[0]] = ''
					else:
						schd_opt_dct[cur_run]['maker'][opt[0]] = opt[1]

				elif self.cur_opt_groups['exe'] == 1:
					opt = line.strip().split('=')
					if len(opt) == 1:
						schd_opt_dct[cur_run]['exe'][opt[0]] = ''
					else:
						schd_opt_dct[cur_run]['exe'][opt[0]] = opt[1]

				elif self.cur_opt_groups['qsub'] == 1:
					opt = line.strip().split('=')
					if len(opt) == 1:
						schd_opt_dct[cur_run]['qsub'][opt[0]] = ''
					else:
						schd_opt_dct[cur_run]['qsub'][opt[0]] = opt[1]

				else:
					opt = line.strip().split('=')

					if len(opt) == 1:
						schd_opt_dct[cur_run][opt[0]] = ''
					else:
						schd_opt_dct[cur_run][opt[0]] = opt[1]

		# Set path to snap hmm file generated as output of another run from this schedule file
		try:
			if not schd_opt_dct['snap']['usehmm'] == 0:
				#if not schd_opt_dct['dir'].endswith('/'):
				#	schd_opt_dct['maker']['snaphmm'] = '{0}{1}*.hmm'.format(schd_opt_dct['dir'], schd_opt_dct[int(schd_opt_dct[cur_run]['snap']['usehmm'])]['name'])
				#else:
				schd_opt_dct['maker']['snaphmm'] = '{0}{1}*.hmm'.format(schd_opt_dct['dir'], schd_opt_dct[int(schd_opt_dct[cur_run]['snap']['usehmm'])]['name'])
		except:
			pass


		return schd_opt_dct


test = MakerSchedule()
test.run_sched()
