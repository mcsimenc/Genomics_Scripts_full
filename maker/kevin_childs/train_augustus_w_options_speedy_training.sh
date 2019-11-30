#! /bin/bash


module load MAKER/r1112
module load BLAT/35

WORKING_DIR=$1
PREVIOUS_INDEX_LOG=$2
AUGUSTUS_SPECIES_NAME=$3
CDNA_FASTA=$4


if [[ -z $WORKING_DIR || -z $PREVIOUS_INDEX_LOG || -z $AUGUSTUS_SPECIES_NAME || -z $CDNA_FASTA ]]; then
    echo "Usage: $0 WORKING_DIR  PREVIOUS_INDEX_LOG  AUGUSTUS_SPECIES_NAME   CDNA_FASTA"
    exit 1
elif [ ! -e $PREVIOUS_INDEX_LOG ]; then
    echo "The previous index log file does not exist: $PREVIOUS_INDEX_LOG"
    exit 1
elif [ ! -e $CDNA_FASTA ]; then
    echo "The cDNA fasta file does not exist: $CDNA_FASTA"
    exit 1
fi

# 1. Convert the maker output to zff format using the maker datastore log file

# Run these commands in $WORKING_DIR.

cd $WORKING_DIR

maker2zff -x 0.2 -l 200 -d $PREVIOUS_INDEX_LOG

# output: genome.ann (ZFF file)
#         genome.dna (fasta file that the coordinates in the zff can be referenced againsted)

# 2. use the fathom  script from snap to get the unique annotations

# Run these commands in $WORKING_DIR

fathom genome.ann genome.dna -categorize 1000

NUMFOUND="`grep -c '>' uni.ann`"

if [ ${NUMFOUND} -gt 299 ]; then
    NUMFOUND=300
fi

TEMPSPLIT=$((NUMFOUND/2))
NUMSPLIT=${TEMPSPLIT/.*}

echo "number found after fathom: $NUMFOUND"
echo "number after split: $NUMSPLIT"

# 3. use Hao's script to convert to genbank format

# Run these commands in $WORKING_DIR

/opt/perl/bin/perl ~/scripts/maker/convert_fathom2genbank.pl uni.ann uni.dna ${NUMFOUND} > ${WORKING_DIR}/augustus.gb


#To get the subset of fastas that correspond to the genes in the genbank file, follow these steps.

perl -e  'while (my $line = <>){ if ($line =~ /^LOCUS\s+(\S+)/) { print "$1\n"; } }'  ${WORKING_DIR}/augustus.gb  >  ${WORKING_DIR}/genbank_gene_list.txt

/home/kchilds/scripts/utilities/get_subset_of_fastas.pl   -l  ${WORKING_DIR}/genbank_gene_list.txt    -f ${WORKING_DIR}/uni.dna  -o  ${WORKING_DIR}/genbank_gene_seqs.fasta

# 4. random split

# Run these commands in $WORKING_DIR

/opt/perl/bin/perl /share/apps/augustus/2.6.1--GCC-4.1.2/scripts/randomSplit.pl ${WORKING_DIR}/augustus.gb ${NUMSPLIT}

# 5. Run autoAug.pl

# Run these commands in $WORKING_DIR

/opt/perl/bin/perl /share/apps/augustus/2.6.1--GCC-4.1.2/scripts/autoAug.pl --species=$AUGUSTUS_SPECIES_NAME --genome=${WORKING_DIR}/genbank_gene_seqs.fasta --trainingset=${WORKING_DIR}/augustus.gb.train --cdna=$CDNA_FASTA

# 6. Run the batch scripts generated by the previous command
# Please start the augustus jobs $WORKING_DIR/autoAug/autoAugPred_abinitio/shells/aug* manually now.
# Either by running them sequentially on a single PC or by submitting these jobs to a compute cluster. When the jobs are done, simply rerun your original command with --useexisting

cd ${WORKING_DIR}/autoAug/autoAugPred_abinitio/shells

# The number of ./aug# scripts is variable.  Run until the new file does not exist.
x=1
while [ -e ./aug${x} ]
do
    echo "A.  $x"
    ./aug${x}
    let x=x+1
done

# 7. Run the next command as indicated by autoAug.pl in step 5.

# When above jobs are finished, continue by running the command autoAug.pl

cd $WORKING_DIR

/opt/perl/bin/perl /share/apps/augustus/2.6.1--GCC-4.1.2/scripts/autoAug.pl --species=$AUGUSTUS_SPECIES_NAME --genome=${WORKING_DIR}/genbank_gene_seqs.fasta --useexisting --hints=${WORKING_DIR}/autoAug/hints/hints.E.gff  -v -v  --index=1

# 8. Run the batch scripts as indicated by autoAug.pl in step 7.

cd ${WORKING_DIR}/autoAug/autoAugPred_hints/shells/

# The number of ./aug# scripts is variable.  Run until the new file does not exist.
let x=1
while [ -e ./aug${x} ]
do
    echo "B.  $x"
    ./aug${x}
    let x=x+1
done

# 9. Run the next command as indicated by autoAug.pl in step 7.

cd $WORKING_DIR

/opt/perl/bin/perl /share/apps/augustus/2.6.1--GCC-4.1.2/scripts/autoAug.pl --species=$AUGUSTUS_SPECIES_NAME --genome=${WORKING_DIR}/genbank_gene_seqs.fasta --useexisting --hints=${WORKING_DIR}/autoAug/hints/hints.E.gff --estali=${WORKING_DIR}/autoAug/cdna/cdna.f.psl -v -v -v  --index=2

# 10. Run the batch scripts generated by autoAug.pl in step 9.

cd ${WORKING_DIR}/autoAug/autoAugPred_hints_utr/shells

# The number of ./aug# scripts is variable.  Run until the new file does not exist.
let x=1
while [ -e ./aug${x} ]
do
    echo "C.  $x"
    ./aug${x}
    let x=x+1
done

# 11. Run the next command

cd $WORKING_DIR

/opt/perl/bin/perl /share/apps/augustus/2.6.1--GCC-4.1.2/scripts/autoAug.pl --species=$AUGUSTUS_SPECIES_NAME --genome=${WORKING_DIR}/genbank_gene_seqs.fasta --useexisting --hints=${WORKING_DIR}/autoAug/hints/hints.E.gff  -v -v -v  --index=3

# 12. Checked sensitivity and specificity

/share/apps/augustus/2.6.1--GCC-4.1.2/bin/augustus --species=$AUGUSTUS_SPECIES_NAME augustus.gb.test

