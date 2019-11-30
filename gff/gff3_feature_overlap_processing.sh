module load genomics/bedops
module load genomics/bedtools

function help {

	echo -e "\n"
	echo -e "gff3_feature_overlap_processing.sh -p output_prefix -gff gff_file"
	echo -e "\n"

}


# Parse command line options
if [ $# == 0 ]
then
	help
fi

while [[ $# > 1 ]]
do
param="$1"

case $param in
	-h|--help) # print help
	help
	;;
	-p|--prefix) # prefix for creating files
	PREFIX="$2"
	shift
	;;
	-gff) # input gff file
	GFF="$2"
	shift
	;;
	*)
	;;
esac
shift
done

gff2bed < $GFF > $PREFIX.bed
intersectBed -a $PREFIX.bed -b $PREFIX.bed -wa -wb > $PREFIX.intersection.bed
~/scripts/bedSelfIntersection2uniqeOverlaps.py -bed $PREFIX.intersection.bed > $PREFIX.intersection.uniqueOverlaps.bed

~/scripts/bedIntersect2percentOverlap.py < $PREFIX.intersection.uniqueOverlaps.bed > $PREFIX.intersection.uniqueOverlaps.percentOverlap

# get other info about genes that overlap (CDS length and AED score)
awk '{print $1}' $PREFIX.intersection.uniqueOverlaps.percentOverlap > $PREFIX.intersection.uniqueOverlaps.percentOverlap.names1
awk '{print $3}' $PREFIX.intersection.uniqueOverlaps.percentOverlap > $PREFIX.intersection.uniqueOverlaps.percentOverlap.names2


awk '{print $1"\t"$2}' $PREFIX.intersection.uniqueOverlaps.percentOverlap > $PREFIX.intersection.uniqueOverlaps.percentOverlap.gene1
awk '{print $3"\t"$4}' $PREFIX.intersection.uniqueOverlaps.percentOverlap > $PREFIX.intersection.uniqueOverlaps.percentOverlap.gene2


# merge summaries
~/scripts/mergeFeatureStats.py -nohead -features $PREFIX.intersection.uniqueOverlaps.percentOverlap.names1 -files geneNames.AED,geneNames.proteinLength > $PREFIX.round2overlaps1.AED.protLength 2>/dev/null
~/scripts/mergeFeatureStats.py -nohead -features $PREFIX.intersection.uniqueOverlaps.percentOverlap.names2 -files geneNames.AED,geneNames.proteinLength > $PREFIX.round2overlaps2.AED.protLength 2>/dev/null

~/scripts/mergeFeatureStats.py -cbind -files $PREFIX.intersection.uniqueOverlaps.percentOverlap.gene1,$PREFIX.round2overlaps1.AED.protLength > $PREFIX.tmp1
~/scripts/mergeFeatureStats.py -cbind -files $PREFIX.intersection.uniqueOverlaps.percentOverlap.gene2,$PREFIX.round2overlaps2.AED.protLength > $PREFIX.tmp2
 ~/scripts/mergeFeatureStats.py -cbind -files $PREFIX.tmp1,$PREFIX.tmp2 | awk '{print $1"\t"$2"\t"$4"\t"$5"\t"$6"\t"$7"\t"$9"\t"$10}' > $PREFIX.intersection.uniqueOverlaps.percentOverlap.AED.protLength

# find is any pair both have 100% overlap
awk '{print ($2==1.000 && $6==1.000) ? $0 : 1 }' $PREFIX.intersection.uniqueOverlaps.percentOverlap.AED.protLength | grep -v '1'

# remove a gene in a pair if it has 100% overlap
awk '{print ($2==1.000 && $6!=1.000) ? $5 : ($2!=1.000 && $6==1.000) ? $1 : $0}' $PREFIX.intersection.uniqueOverlaps.percentOverlap.AED.protLength | grep -vE '\s.*\s' > $PREFIX.overlappedGenesToKeep

# of the pairs where both genes have <100% overlap, keep the one with lower AED
awk '{print ($2==1.000 && $6!=1.000) ? $5 : ($2!=1.000 && $6==1.000) ? $1 : $0}' $PREFIX.intersection.uniqueOverlaps.percentOverlap.AED.protLength | grep -E '\s.*\s' | awk '{print ($3 == $7) ? $0 : ($3 < $7) ? $1 :  $5}' | grep -vE '\s.*\s' >> $PREFIX.overlappedGenesToKeep

# of the pairs where both genes have <100% overlap and both have the same AED, keep the gene with less overlap
awk '{print ($2==1.000 && $6!=1.000) ? $5 : ($2!=1.000 && $6==1.000) ? $1 : $0}' $PREFIX.intersection.uniqueOverlaps.percentOverlap.AED.protLength | grep -E '\s.*\s' | awk '{print ($3 == $7) ? $0 : ($3 < $7) ? $1 :  $5}' | grep -E '\s.*\s' | awk '{print ($2 < $6) ? $1 : $5 }' >> $PREFIX.overlappedGenesToKeep


