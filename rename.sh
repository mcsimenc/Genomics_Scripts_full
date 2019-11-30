for i in *.fastq.gz
do
 echo working with $i
 basename="$(basename $i .fastq.gz)"
 mv $i ${basename}.fastq.gz
done
