#!/usr/bin/env python

#from subprocess import check_output # Python >= 2.7
import subprocess # Python 2.6
import sys
from re import findall

#qstat = str(check_output(['qstat', '-n'])) # Python >= 2.7
qstat = str(subprocess.Popen(['qstat', '-n'], stdout=subprocess.PIPE).communicate()[0]) # Python 2.6

nodes_used = findall('kepler-0-\d+', qstat)
nodes_all = ['kepler-0-0','kepler-0-1','kepler-0-2','kepler-0-3','kepler-0-4','kepler-0-5','kepler-0-6','kepler-0-7','kepler-0-8','kepler-0-9','kepler-0-10','kepler-0-11','kepler-0-12','kepler-0-13','kepler-0-14','kepler-0-15','kepler-0-16','kepler-0-17','kepler-0-18','kepler-0-19','kepler-0-20','kepler-0-21','kepler-0-22','kepler-0-23','kepler-0-24','kepler-0-25','kepler-0-26','kepler-0-27','kepler-0-28','kepler-0-29','kepler-0-30','kepler-0-31','kepler-0-32','kepler-0-33','kepler-0-34','kepler-0-35']

nodes_avail = {'kepler-0-0':(32,'performance'),
		'kepler-0-1':(32,'performance'),
		'kepler-0-2':(40,'q40'),
		'kepler-0-3':(40,'q40'),
		'kepler-0-4':(40,'q40'),
		'kepler-0-5':(40,'q40'),
		'kepler-0-6':(40,'q40'),
		'kepler-0-7':(40,'q40'),
		'kepler-0-8':(40,'q40'),
		'kepler-0-9':(40,'q40'),
		'kepler-0-10':(24,'q24'),
		'kepler-0-11':(24,'q24'),
		'kepler-0-12':(24,'q24'),
		'kepler-0-13':(24,'q24'),
		'kepler-0-14':(24,'q24'),
		'kepler-0-15':(24,'q24'),
		'kepler-0-16':(24,'q24'),
		'kepler-0-17':(24,'q24'),
		'kepler-0-18':(24,'q24'),
		'kepler-0-19':(24,'q24'),
		'kepler-0-20':(24,'q24'),
		'kepler-0-21':(24,'q24'),
		'kepler-0-22':(24,'q24'),
		'kepler-0-23':(24,'q24'),
		'kepler-0-24':(24,'q24'),
		'kepler-0-25':(24,'q24'),
		'kepler-0-26':(24,'q24'),
		'kepler-0-27':(24,'q24'),
		'kepler-0-28':(24,'q24'),
		'kepler-0-29':(24,'q24'),
		'kepler-0-30':(24,'q24'),
		'kepler-0-31':(24,'q24'),
		'kepler-0-32':(24,'q24'),
		'kepler-0-33':(24,'q24'),
		'kepler-0-34':(24,'q24'),
		'kepler-0-35':(24,'q24')}



#node_counts = { node:0 for node in set(nodes) } # Python >= 2.7
node_counts = dict((node, 0) for node in nodes_all) # Python 2.6


for node in nodes_used:
	node_counts[node] += 1


nodes_sorted = [ (key, int(key.split('-')[-1])) for key in node_counts.keys() ]

nodes_sorted.sort(key=lambda x:x[1])

#print('-------------------------------')
#print('node          used   available')
#print('-------------------------------')

lastQueue = None
for node in nodes_sorted:

	queue = nodes_avail[node[0]][1]
	if  queue != lastQueue:
		print('-------------------------------')
		print(' {0}'.format(queue))
		print('-------------------------------')
		if lastQueue == None:
			print('node          used   available')
			print('------------ ------ -----------')
	lastQueue = queue

	count = node_counts[node[0]]
	print('{0}\t{1}\t{2}'.format(node[0], count, nodes_avail[node[0]][0]-count))
