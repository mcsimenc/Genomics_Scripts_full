#!/bin/bash
#PBS -k oe
#PBS -l nodes=1:ppn=40
#PBS -N scythe-seqqs-sickle_trimmed
#PBS -q default
#PBS -j oe
#PBS -m ea
#PBS -M mcsimenc@csu.fullerton.edu

module load genomics/seqqs
module load genomics/sickle
module load genomics/scythe

# trim.sh - generic, slightly insane paired end quality trimming script
# Vince Buffalo <vsbuffaloAAAAAA@gmail.com> (sans poly-A)
set -e
set -u

## pre-config
ADAPTERS=illumina_adapters.fa
SAMPLE_NAME=L2
IN1=L2_R1.fastq.gz
IN2=L2_R2.fastq.gz

## presets
PRIOR=0.05
QUAL_THRESH=20

time (sickle pe -t sanger -q $QUAL_THRESH \
    -f <(seqqs -e -p raw_${SAMPLE_NAME}_R1 $IN1 | scythe -a $ADAPTERS -p $PRIOR - 2> ${SAMPLE_NAME}_R1_scythe.stderr) \
    -r <(seqqs -e -p raw_${SAMPLE_NAME}_R2 $IN2 | scythe -a $ADAPTERS -p $PRIOR - 2> ${SAMPLE_NAME}_R2_scythe.stderr) \
    -o >(seqqs -e -p trimmed_${SAMPLE_NAME}_R1 - | gzip > ${SAMPLE_NAME}_R1_trimmed.fq.gz) \
    -p >(seqqs -e -p trimmed_${SAMPLE_NAME}_R2 - | gzip > ${SAMPLE_NAME}_R2_trimmed.fq.gz) \
    -s >(seqqs -e -p trimmed_${SAMPLE_NAME}_singles - | gzip > ${SAMPLE_NAME}_singles_trimmed.fq.gz) 2> ${SAMPLE_NAME}_sickle.stderr)


# Usage: sickle <command> [options]
# 
# Command:
# pe	paired-end sequence trimming
# se	single-end sequence trimming
# 
# --help, display this help and exit
# --version, output version information and exit
# 
# $ sickle pe
# 
# If you have separate files for forward and reverse reads:
# Usage: sickle pe [options] -f <paired-end forward fastq file> -r <paired-end reverse fastq file> -t <quality type> -o <trimmed PE forward file> -p <trimmed PE reverse file> -s <trimmed singles file>
# 
# If you have one file with interleaved forward and reverse reads:
# Usage: sickle pe [options] -c <interleaved input file> -t <quality type> -m <interleaved trimmed paired-end output> -s <trimmed singles file>
# 
# If you have one file with interleaved reads as input and you want ONLY one interleaved file as output:
# Usage: sickle pe [options] -c <interleaved input file> -t <quality type> -M <interleaved trimmed output>
# 
# Options:
# Paired-end separated reads
# --------------------------
# -f, --pe-file1, Input paired-end forward fastq file (Input files must have same number of records)
# -r, --pe-file2, Input paired-end reverse fastq file
# -o, --output-pe1, Output trimmed forward fastq file
# -p, --output-pe2, Output trimmed reverse fastq file. Must use -s option.
# 
# Paired-end interleaved reads
# ----------------------------
# -c, --pe-combo, Combined (interleaved) input paired-end fastq
# -m, --output-combo, Output combined (interleaved) paired-end fastq file. Must use -s option.
# -M, --output-combo-all, Output combined (interleaved) paired-end fastq file with any discarded read written to output file as a single N. Cannot be used with the -s option.
# 
# Global options
# --------------
# -t, --qual-type, Type of quality values (solexa (CASAVA < 1.3), illumina (CASAVA 1.3 to 1.7), sanger (which is CASAVA >= 1.8)) (required)
# -s, --output-single, Output trimmed singles fastq file
# -q, --qual-threshold, Threshold for trimming based on average quality in a window. Default 20.
# -l, --length-threshold, Threshold to keep a read based on length after trimming. Default 20.
# -x, --no-fiveprime, Don't do five prime trimming.
# -n, --truncate-n, Truncate sequences at position of first N.
# -g, --gzip-output, Output gzipped files.
# --quiet, do not output trimming info
# --help, display this help and exit
# --version, output version information and exit

# $ seqqs
# Usage: seqqs [options] <in.fq>
# 
# Options: -q    quality type, either illumina, solexa, or sanger (default: sanger)
#          -p    prefix for output files (default: none)
#          -k    hash k-mers of length k (default: off)
#          -e    emit reads to stdout, for pipelining (default: off)
#          -f    input is FASTA (no quality lines, default: off)
#          -i    input is interleaved, output statistics per each file (default: off)
#          -s    strict; some warnings become errors (default: off)
# Arguments:  <in.fq> or '-' for stdin.
# 
# Output:
# <prefix> is output prefix name. The following output files will be created:
# <prefix>_qual.txt:  quality distribution by position matrix
# <prefix>_nucl.txt:  nucleotide distribution by position matrix
# <prefix>_len.txt:   length distribution by position matrix
# <prefix>_kmer.txt:  k-mer distribution by position matrix
# If -i is used, these will have "_1.txt" and "_2.txt" suffixes.
