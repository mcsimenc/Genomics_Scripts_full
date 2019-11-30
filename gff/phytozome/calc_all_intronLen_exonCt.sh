#!/bin/bash


module load genometools

for file in `find noCDS_GFF -name "*gene*gff3"`; do gt gff3 -sort -retainids < $file > sortedGFFs/${file##*/}.sorted 2>sortedGFFs_err/${file##*/}.gt_gff3_sort.err; done

for file in `ls sortedGFFs`; do ./gff2intronLengthExonCount.py < sortedGFFs/${file} > intronLengthsExonCounts/${file}.intronLengths 2>intronLengthsExonCounts/${file}.intronCounts; done
