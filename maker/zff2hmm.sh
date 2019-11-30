#!/bin/bash

module load genomics/snap
module load genomics/maker

fathom ./genome.ann ./genome.dna -categorize 1000
fathom ./uni.ann ./uni.dna -export 1000 -plus
forge ./export.ann ./export.dna
hmm-assembler.pl ./genome . > snap.hmm
fathom genome.ann genome.dna -gene-stats > fathom.stats
