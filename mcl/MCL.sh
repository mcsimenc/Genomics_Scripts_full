#!/bin/bash

function help {

	echo -e "\r"
	echo -e "Usage:\r"
	echo -e "------------\r"
	echo -e "MCL.sh -blast <blast_output_file>\r"
	echo -e "\r"
	echo -e "\r"
	echo -e "Description:\r"
	echo -e "------------\r"
	echo -e "Run MCL in MCL-edge. Assumes MCL-edge is available as modulefile named 'local/mcl'.\r"
	echo -e "\r"
	echo -e "\r"
	echo -e "Options:\r"
	echo -e "------------\r"
	echo -e "-blast		blast output file in tabular format with no comment lines.\r"
	echo -e "-procs		Number of processors for each mcl job submission.\r"
	echo -e "-name		Job name for TORQUE job.\r"
	echo -e "-email		Email for TORQUE job.\r"
	echo -e "-queue		Queue for TORQUE job.\r"
	echo -e "\r"

}



# Parse command line options
if [ $# == 0 ]
then
	help
	exit
fi

while [[ $# > 0 ]]
do
param="$1"

case $param in
	-h|--help) # print help
	help
	;;
	-blast) # blast table input file
	BLAST_TABLE="$2"
	shift
	;;
	-p|-procs) # num procs
	PROCS="$2"
	shift
	;;
	-n|-name) # do not execute call, but write to logfile
	JOBNAME="$2"
	shift
	;;
	-e|-email) # note associated with this call for logfile
	EMAIL="$2"
	shift
	;;
	-q|-queue) # write output to logfile
	QUEUE=$2
	shift
	;;
	*)
	;;
esac
shift
done


#if [ -z ${LOGPATH+x} ]
#then
#	LOGPATH=`cat /home/derstudent/scripts/auto_logger/logfile_path`
#else
#	echo $LOGPATH > /home/derstudent/scripts/auto_logger/logfile_path
#fi

# convert blastn output  to abc format for mcl
cut -f 1,2,11 $BLAST_TABLE > ${BLAST_TABLE}.abc

# create network for mcl
module load local/mcl
mcxload -abc ${BLAST_TABLE}.abc --stream-mirror --stream-neg-log10 -stream-tf "ceil(200)" -o ${BLAST_TABLE}.mci -write-tab ${BLAST_TABLE}.tab

cwd=`pwd`


echo "#!/bin/bash" >> call_mcl.qsub
echo "#PBS -k oe" >> call_mcl.qsub
echo "#PBS -N ${JOBNAME}" >> call_mcl.qsub
echo "#PBS -q ${QUEUE}" >> call_mcl.qsub
echo "#PBS -j n" >> call_mcl.qsub
echo "#PBS -m ea" >> call_mcl.qsub
echo "#PBS -M ${EMAIL}" >> call_mcl.qsub
echo "#PBS -l nodes=1:ppn=${PROCS}" >> call_mcl.qsub
echo "" >> call_mcl.qsub
echo "" >> call_mcl.qsub
echo "cd $cwd" >> call_mcl.qsub
echo "" >> call_mcl.qsub
echo "# load mcl" >> call_mcl.qsub
echo "module load local/mcl" >> call_mcl.qsub
echo "" >> call_mcl.qsub
echo "# run mcl" >> call_mcl.qsub
echo "mcl ${BLAST_TABLE}.mci -I 1.4 -use-tab ${BLAST_TABLE}.tab -te ${PROCS} 1>>mcl.stdout 2>>mcl.stderr" >> call_mcl.qsub
echo "mcl ${BLAST_TABLE}.mci -I 2 -use-tab ${BLAST_TABLE}.tab -te ${PROCS} 1>>mcl.stdout 2>>mcl.stderr" >> call_mcl.qsub
echo "mcl ${BLAST_TABLE}.mci -I 4 -use-tab ${BLAST_TABLE}.tab -te ${PROCS} 1>>mcl.stdout 2>>mcl.stderr" >> call_mcl.qsub
echo "mcl ${BLAST_TABLE}.mci -I 6 -use-tab ${BLAST_TABLE}.tab -te ${PROCS} 1>>mcl.stdout 2>>mcl.stderr" >> call_mcl.qsub


qsub call_mcl.qsub
