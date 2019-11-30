#!/bin/bash


# This script creates a hmm file for use in training SNAP based on
# MAKER output
#
# Usage:
#
# maker2hmm.sh [working_directory]
#

cd $1

# Combines MAKER outputs into a single GFF file
gff3_merge -d p_ctg_master_datastore_index.log

# Converts GFF file to ZFF file
maker2zff p_ctg.all.gff

# Writes annotation stats to file
fathom genome.ann genome.dna -gene-stats > genome.stats

# Creates gene models based on annotations + flanking 1000bp regions
fathom -categorize 1000 genome.ann genome.dna
fathom uni.ann uni.dna -export 1000 -plus
forge export.ann export.dna

# Creates HMM file
hmm-assembler.pl falcon.asm.1.0 . > falcon1.0_mkr.hmm
