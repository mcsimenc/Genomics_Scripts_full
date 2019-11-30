#!/bin/bash

function help {

	echo -e "\r"
	echo -e "Usage:\r"
	echo -e "------------\r"
	echo -e "circos-stackedRepeatHist.sh -gff <input.gff> -out <string> -window <int>"
	echo -e "\r"
	echo -e "\r"
	echo -e "Description:\r"
	echo -e "------------\r"
	echo -e "Creates a circos data file for a stacked hist for the input gff\r"
	echo -e "which is expected to be of repeats as Azolla repeats v1.4.1\r"
	echo -e "\r"
	echo -e "\r"
	echo -e "Options: (all of these are required)\r"
	echo -e "------------\r"
	echo -e "-gff		Input repeat GFF3 formatted like Azolla repeats v1.3.\r"
	echo -e "-out		Output filename. Other files will also be created\r"
	echo -e "-scafLens	Scaffold lengths\r"
	echo -e "-scafList	Limit output to these scaffolds\r"
	echo -e "-window		Window size in bp\r"
	echo -e "\r"
	exit

}



# Parse command line options
if [ $# == 0 ]
then
	help
fi

while [[ $# > 0 ]]
do
param="$1"

case $param in
	-h|--help) # print help
	help
	;;
	-gff) # setting log file
	GFF="$2"
	shift
	;;
	-out) # call to be made
	OUT="$2"
	shift
	;;
	-window) # do not execute call, but write to logfile
	WINDOW="$2"
	shift
	;;
	-scafLens) # do not execute call, but write to logfile
	SCAFLENS="$2"
	shift
	;;
	-scafList) # do not execute call, but write to logfile
	SCAFLIST="$2"
	shift
	;;
	*)
	;;
esac
shift
done

~/scripts/gff/gffAnnotateRepeats.py -circos < $GFF

mkdir repeat-composition

mv Copia.gff repeat-composition/
mv DNAtransposon.gff repeat-composition/
mv Gypsy.gff repeat-composition/
mv Other.gff repeat-composition/
mv OtherRetrotransposon.gff repeat-composition/
mv Simple.gff repeat-composition/
mv RNA.gff repeat-composition/

cd repeat-composition/

for file in `ls *gff`; do ~/scripts/gff/gff2circos-heatmap.py -gff $file -scaflens ../$SCAFLENS -window $WINDOW -scafList ../$SCAFLIST > ${file}.heatmap-${WINDOW}kb; done
for file in `ls *kb`; do awk '{print $4}' $file > ${file}.val; done

paste -d "," Copia.gff.heatmap-*kb Gypsy.gff.heatmap-*.val OtherRetrotransposon.gff.heatmap-*.val DNAtransposon.gff.heatmap-*.val RNA.gff.heatmap-*.val Simple.gff.heatmap-*.val  Other.gff.heatmap-*.val > ../$OUT
