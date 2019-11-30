#!/usr/bin/env python3


# Converts genbank format files to fasta format files
# USAGE: gb2fasta.py <genbank>

import sys
from Bio import SeqIO

input_file = sys.argv[1]
output_file = '{0}.fasta'.format(input_file)


SeqIO.convert(input_file, 'genbank', output_file, 'fasta')
