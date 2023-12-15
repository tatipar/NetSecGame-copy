#!/bin/bash

PATH_REPO=`git rev-parse --show-toplevel` # path of the top-level directory

cd ${PATH_REPO}/results/

for result in `ls`; do
	cd $result/
	for dirname in `ls -d */`; do 
    		base1=`echo $dirname | awk -F'_' '{print $2"_"$3}'`
    		base2=`basename $base1 /`
    		grep "Generation" results_$base2/results_$base2.txt | awk '{print $3}' >> number_generations
    		grep "score" results_$base2/results_$base2.txt | awk '{print $4}' >> score_last_generation
    		grep "time" results_$base2/results_$base2.txt | awk '{print $2}' >> time_per_generation
	done
	cd ../
done	


#for dirname in `ls -d */`; do base1=`echo $dirname | awk -F'_' '{print $2"_"$3}'`; base2=`basename $base1 /`; grep "score" results_$base2/results_$base2.txt | awk '{print $4}'; done
