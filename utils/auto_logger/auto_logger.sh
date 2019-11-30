#!/bin/bash

function help {

	echo -e "\r"
	echo -e "Usage:\r"
	echo -e "------------\r"
	echo -e "auto_logger.sh [-set <string>] [-c \"<string>\"] [-n \"<string>\"]\r"
	echo -e "\r"
	echo -e "Current logfile: `cat /home/derstudent/scripts/utils/auto_logger/logfile_path`\r"
	echo -e "\r"
	echo -e "\r"
	echo -e "Description:\r"
	echo -e "------------\r"
	echo -e "Writes these lines to a log file in this relative order.\r"
	echo -e "\r"
	echo -e "\tnote (optional)\r"
	echo -e "\tdate\r"
	echo -e "\tcwd\r"
	echo -e "\tfunction call\r"
	echo -e "\tfunction call output (optional)\r"
	echo -e "\r"
	echo -e "\r"
	echo -e "Also execute function call...or not, if -s is specified.\r"
	echo -e "\r"
	echo -e "*Backticks expand before call and may cause problems.\r"
	echo -e "*You may need to escape special characters. e.g. you'll need\r"
	echo -e "to escape $ if using awk as in awk '{print \$3}' and you don't\r"
	echo -e "want $3 to expand before running the command\r"
	echo -e "\r"
	echo -e "Options:\r"
	echo -e "------------\r"
	echo -e "-set	The  path to the log file to write to. Default is last set path.\r"
	echo -e "-c	The function call to execute (inside double quotes)\r"
	echo -e "-n	A note to append to logfile.\r"
	echo -e "-s	Silent mode. Do not execute call, but write to logfile.\r"
	echo -e "-o	Write function call stdout to logfile.\r"
	echo -e "\r"

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
	-set) # setting log file
	LOGPATH="$2"
	shift
	;;
	-c|--call) # call to be made
	CALL="$2"
	shift
	;;
	-s|--silent) # do not execute call, but write to logfile
	SILENT="SILENT"
	shift
	;;
	-n|--note) # note associated with this call for logfile
	NOTE="$2"
	shift
	;;
	-o|--output) # write output to logfile
	OUTPUT="TRUE"
	shift
	;;
	*)
	;;
esac
shift
done


if [ -z ${LOGPATH+x} ]
then
	LOGPATH=`cat /home/derstudent/scripts/utils/auto_logger/logfile_path`
else
	echo $LOGPATH > /home/derstudent/scripts/utils/auto_logger/logfile_path
fi


# no call
if [ -z ${CALL+x} ]
then
	# write note
	if [ -z ${NOTE+x} ]
	then
		:
	else
		echo "${NOTE}" >> "${LOGPATH}"
		echo "" >> "${LOGPATH}"
	fi
# with call
else
	# write note
	if [ -z ${NOTE+x} ]
	then
		:
	else
		echo "${NOTE}" >> "${LOGPATH}"
	fi

	# write date
	echo `date` >> "${LOGPATH}"

	# write cwd
	echo `pwd` >> "${LOGPATH}"

	# write call
	echo $CALL >> "${LOGPATH}"
	
	if [ -n "$OUTPUT" ]
	then
		:
	else
	# write newline
		echo "" >> "${LOGPATH}"
	fi
fi

if [ -n "$SILENT" ]
then
	:
else
	# perform call
	if [ -n "$OUTPUT" ]
	then
		eval $CALL | tee -a $LOGPATH
		echo "" >> "${LOGPATH}"
	else
		eval $CALL
	fi
fi
