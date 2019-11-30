#!/bin/bash


#FOR GFF:

~/scripts/repeatmasker/summarize_repeat_masker_gff.py *gff #-db ~/data/other/repbase_viridiplantae_2017-05-22.embl

for file in `ls *summary*`; do sort -k3,3 -n $file > ${file}.sorted; done

echo "TOTAL bp in full"
grep -v '^Name' *full.sorted | awk '{print $3}' | ~/scripts/utils/mean_median_min_max.py
echo "TOTAL bp in short"
grep -v '^Name' *_short.sorted | awk '{print $3}' | ~/scripts/utils/mean_median_min_max.py

echo "TOTAL bp in gff"
grep -v '^#' *gff | awk '{print $5-$4+1}' | ~/scripts/utils/mean_median_min_max.py



# ------

#FOR BED

#~/scripts/repeats/summarize_repeat_masker_gff.py *bed -bed #-db /home/derstudent/data/other/RepBase/RepBase_viridiplantae_20170522/repbase_viridiplantae_2017-05-22.embl
#
#for file in `ls *summary*`; do sort -k3,3 -n $file > ${file}.sorted; done
#
#echo "TOTAL bp in full"
#grep -v '^Name' *full.sorted | awk '{print $3}' | ~/scripts/mean_median_min_max.py
#echo "TOTAL bp in short"
#grep -v '^Name' *_short.sorted | awk '{print $3}' | ~/scripts/mean_median_min_max.py
#echo "TOTAL bp in supershort"
#grep -v '^Name' *supershort.sorted | awk '{print $3}' | ~/scripts/mean_median_min_max.py
#echo "TOTAL bp in gff"
#grep -v '^#' *bed | awk '{print $3-$2}' | ~/scripts/mean_median_min_max.py
