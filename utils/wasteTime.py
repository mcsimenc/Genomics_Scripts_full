#!/usr/bin/env python

# The purpose of this script is to print something to stdout so I don't get disconnected from Kepler via a timeout on Orca (I think this is what's happening) when I'm connected from off campus. It prints the current date and time every 51 seconds.

from time import strftime, gmtime, sleep

while True:
	print(strftime('%A, %B %d, %H:%M %S seconds', gmtime()))
	sleep(51)
