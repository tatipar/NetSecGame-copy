#!/bin/bash

PATH_REPO=`git rev-parse --show-toplevel` # path of the top-level directory

ALL_RESULTS=${PATH_REPO}/agents/genetic/results/
cd ${ALL_RESULTS}

for result in `ls`; do
	cd $result/
	mkdir analysis
	for  i in {0..9}; do
		grep "Generation" results_$(printf "%02d" "$i")/results_$(printf "%02d" "$i").txt | awk '{print $3}' >> analysis/number_generations
		grep -oP 'Best sequence score:  \[\K[0-9.]*' results_$(printf "%02d" "$i")/results_$(printf "%02d" "$i").txt | awk '{print $1}' >> analysis/best_score_last_generation
		grep "time" results_$(printf "%02d" "$i")/results_$(printf "%02d" "$i").txt | awk '{print $2}' >> analysis/total_time
	done
	PATH_RESULTS=${ALL_RESULTS}/${result}
	python3 -u ${PATH_REPO}/agents/genetic/python/analysis.py ${PATH_RESULTS} >> analysis/analysis.txt 
	cd ../
done	


