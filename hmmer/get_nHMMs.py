#!/usr/bin/env python3

import sys

n = int(sys.argv[1])

count = 0
for line in sys.stdin:
	if line.strip() == '//':
		count += 1
	print(line, end='')
	if count == n:
		break
