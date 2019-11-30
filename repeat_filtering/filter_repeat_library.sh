#!/bin/bash

function help {

	echo -e "\n"
	echo -e "\t\tUsage:\r"
	echo -e "\t\t------------\r"
	echo -e "\t\tfilter_repeat_library.sh -b <blast_output> [options]\n"

	echo -e "\t\tDescription:\r"
	echo -e "\t\t------------\r"
	echo -e "\t\tFrom the blastx default output (tested with BLAST+ v2.2.31+), identify the highest-scoring alignment\r"
	echo -e "\t\tfor all queries (repeat predictions) and get annotations from PlantTribes 1.1 OrthoMCL, Orthofinder,\r"
	echo -e "\t\tand GFam orthogroups for the set of subjects (PlantTribes 1.1 genes) that overlap queries by amounts\r"
	echo -e "\t\tspecified by -f and -c options. An additional file with PlantTribes genes not belonging to any\r"
	echo -e "\t\torthogroup is output. blastx output is first converted using blast_parser.pl\n"

	echo -e "\t\tOptions:\r"
	echo -e "\t\t------------\r"
	echo -e "\t\t-b,--blast_output <filepath>		File containing default blastx output\r"
	echo -e "\t\t-bn,--basename <str>			Desired basename for output files. Defaults to -b or -bp if unspecified.\r"
	echo -e "\t\t-bp,--blast_parsed <filepath>		File containing blastx output parsed by blast_parser.pl. Overrides -b\r"
	echo -e "\t\t-c,--ceiling <number>  			Find annotations for genes overlapping repeats by no more than this %\r"
	echo -e "\t\t\t\t\t\t\tof length of the repeat.\r"
	echo -e "\t\t-f,--floor <number>  			Find annotations for genes overlapping repeats by no less than this %\r"
	echo -e "\t\t\t\t\t\t\tof length of the repeat.\r"
	echo -e "\t\t-ofmap,--orthofinder_map <filepath> 	View script for defaults\r"
	echo -e "\t\t-ofann,--orthofinder_annotation <filepath> View script for defaults\r"
	echo -e "\t\t-ommap,--orthomcl_map <filepath> 	View script for defaults\r"
	echo -e "\t\t-omann,--orthomcl_annotation <filepath>View script for defaults\r"
	echo -e "\t\t-gfmap,--gfam_map <filepath> 		View script for defaults\r"
	echo -e "\t\t-gfann,--gfam_annotation <filepath> 	View script for defaults\n"

	exit

}

# Set defaults
CEILING=100
FLOOR=0
ORTHOFINDER_MAP=/home/derstudent/data/other/PlantTribes/22Gv1.1/annot/orthofinder.list
ORTHOFINDER_ANNOTATION=/home/derstudent/data/other/PlantTribes/22Gv1.1/annot/orthofinder.avg_evalue.summary
ORTHOMCL_MAP=/home/derstudent/data/other/PlantTribes/22Gv1.1/annot/orthomcl.list
ORTHOMCL_ANNOTATION=/home/derstudent/data/other/PlantTribes/22Gv1.1/annot/orthomcl.avg_evalue.summary
GFAM_MAP=/home/derstudent/data/other/PlantTribes/22Gv1.1/annot/gfam.list
GFAM_ANNOTATION=/home/derstudent/data/other/PlantTribes/22Gv1.1/annot/gfam.avg_evalue.summary

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
	-b|--blast_output) # default blast output
	BLAST_OUTPUT="$2"
	shift
	;;
	-bn|--basename) # basename for output files
	BASENAME="$2"
	shift
	;;
	-bp|--blast_parsed) # parsed blastx output. if -b is also specified when -bp is specified, -b will be ignored
	BLAST_PARSED="$2"
	shift
	;;
	-c|--ceiling) # don't process alignments for which the repeat prediction was overlapped by more that this much
	CEILING="$2"
	shift
	;;
	-f|--floor) # don't process alignments for which the repeat prediction was overlapped by less that this much
	FLOOR="$2"
	shift
	;;
	-ofmap|--orthofinder_map) # path to PlantTribes v1.1 mapping of gene names to Orthofinder orthologous groups
	ORTHOFINDER_MAP="$2"
	shift
	;;
	-ofann|--orthofinder_annotation) # path to PlantTribes v1.1 Orthofinder orthologous groups annotations
	ORTHOFINDER_ANNOTATION="$2"
	shift
	;;
	-gfmap|--gfam_map) # path to PlantTribes v1.1 mapping of gene names to GFam orthologous groups
	GFAM_MAP="$2"
	shift
	;;
	-gfann|--gfam_annotation) # path to PlantTribes v1.1 GFam orthologous groups annotations
	GFAM_ANNOTATION="$2"
	shift
	;;
	-ommap|--orthofinder_map) # path to PlantTribes v1.1 mapping of gene names to OrthoMCL orthologous groups
	ORTHOMCL_MAP="$2"
	shift
	;;
	-omann|--orthofinder_annotation) # path to PlantTribes v1.1 OrthoMCL orthologous groups annotations
	ORTHOMCL_ANNOTATION="$2"
	shift
	;;
	*)
	;;
esac
shift
done

# if basename is unspecified, set as blast_output or blast_parsed
if [ -z ${BASENAME+x} ] 
then
	if [ -z ${BLAST_PARSED+x} ]
	then
		BASENAME=${BLAST_OUTPUT}
	else
		BASENAME=${BLAST_PARSED}
	fi
else
	:
fi
		


touch ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

module load genomics/blastparser
module load genomics/perl
module load genomics/derlab


if [ -z ${BLAST_PARSED+x} ]
then
	# convert default blast output
	echo "blast_parser.pl" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

	perl `which blast_parser.pl` < ${BASENAME} > ${BASENAME}.parsed 2>>${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

	# get % overlap stats for blast output
	echo "blast_parser.pl_output_stats.py" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

	blast_parser.pl_output_stats.py -s -sbjq -f ${FLOOR} -c ${CEILING} < ${BASENAME}.parsed > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.pairs 2>>${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

else
	# get % overlap stats for blast output
	echo "blast_parser.pl_output_stats.py" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

	blast_parser.pl_output_stats.py -s -sbjq -f ${FLOOR} -c ${CEILING} < ${BLAST_PARSED} > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.pairs 2>>${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
fi

# get orthologous group annotations
echo "cat" >>${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.pairs | awk -F '\t' '{print $1"\t"$2}' > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs 2>> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

echo "GetPlantTribesOGinfo.py OrthoMCL summary" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
GetPlantTribesOGinfo.py < ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs \
			-go \
			-s \
			-q \
			-l ${ORTHOMCL_MAP} \
			-a ${ORTHOMCL_ANNOTATION} \
			> ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.summary \
			2>> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

echo "GetPlantTribesOGinfo.py OrthoMCL annotation" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
GetPlantTribesOGinfo.py < ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs \
			-go \
			-q \
			-l ${ORTHOMCL_MAP} \
			-a ${ORTHOMCL_ANNOTATION} \
			> ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.annotation \
			2>> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

echo "GetPlantTribesOGinfo.py Orthofinder summary" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
GetPlantTribesOGinfo.py < ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs \
			-go \
			-s \
			-q \
			-l ${ORTHOFINDER_MAP} \
			-a ${ORTHOFINDER_ANNOTATION} \
			> ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.summary \
			2>> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

echo "GetPlantTribesOGinfo.py Orthofinder annotation" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
GetPlantTribesOGinfo.py < ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs \
			-go \
			-q \
			-l ${ORTHOFINDER_MAP} \
			-a ${ORTHOFINDER_ANNOTATION} \
			> ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.annotation \
			2>> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

echo "GetPlantTribesOGinfo.py GFam summary" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
GetPlantTribesOGinfo.py < ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs \
			-go \
			-s \
			-q \
			-l ${GFAM_MAP} \
			-a ${GFAM_ANNOTATION} \
			> ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.summary \
			2>> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr

echo "GetPlantTribesOGinfo.py GFam annotation" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
GetPlantTribesOGinfo.py < ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs \
			-go \
			-q \
			-l ${GFAM_MAP} \
			-a ${GFAM_ANNOTATION} \
			> ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.annotation \
			2>> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr


cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.summary | awk -F '\t' '{print $5}' | sed 's/;/\n/g'  > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.seqNames
cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.summary | awk -F '\t' '{print $3}' | sed 's/;/\n/g'  > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.geneNames

cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.summary | awk -F '\t' '{print $5}' | sed 's/;/\n/g'  > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.seqNames
cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.summary | awk -F '\t' '{print $3}' | sed 's/;/\n/g'  > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.geneNames

cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.summary | awk -F '\t' '{print $5}' | sed 's/;/\n/g'  > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.seqNames
cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.summary | awk -F '\t' '{print $3}' | sed 's/;/\n/g'  > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.geneNames

cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.seqNames > tmp.allSeqNames
cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.seqNames >> tmp.allSeqNames
cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.seqNames >> tmp.allSeqNames

cat tmp.allSeqNames | tr -d '\r' | sort | uniq > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.allseqNames

rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.seqNames
rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.seqNames
rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.seqNames
rm tmp.allSeqNames


# Find out which genes are not included in any PlantTribes v1.1 orthogroup annotation
echo "diffLines.py" >> ${BASENAME}.repeatFiltering.${FLOOR}-${CEILING}_percentQueryOverlap.stderr
cat ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs | awk -F '\t' '{print $1}' > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.geneNames
diffLines.py ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.geneNames ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.geneNames ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.geneNames ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.geneNames > ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.noOrthogroup.geneNames
rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.geneNames
rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.alignmentPairs

rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.GFam.geneNames
rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.Orthofinder.geneNames
rm ${BASENAME}.highestscoreAlignment_${FLOOR}-${CEILING}_percentQueryOverlap.OrthoMCL.geneNames
