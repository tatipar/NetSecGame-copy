#!/bin/bash

## Script que automatiza el analisis de resultados obtenidos



PATH_REPO=`git rev-parse --show-toplevel` # path of the top-level directory

ALL_RESULTS=${PATH_REPO}/agents/genetic/results/
cd ${ALL_RESULTS}

for result in `ls`; do
	cd $result/
	mkdir analysis
	for  i in {0..9}; do
		grep "Generation" results_$(printf "%02d" "$i")/results_$(printf "%02d" "$i").txt | awk '{print $3}' >> analysis/number_generations
		grep 'Best sequence score:' results_$(printf "%02d" "$i")/results_$(printf "%02d" "$i").txt | awk '{gsub(/[\[\]]/, ""); print $4}' >> analysis/best_score_last_generation
		grep "time" results_$(printf "%02d" "$i")/results_$(printf "%02d" "$i").txt | awk '{print $2}' >> analysis/total_time
	done
	PATH_RESULTS=${ALL_RESULTS}/${result}
	python3 -u ${PATH_REPO}/agents/genetic/python/analysis.py ${PATH_RESULTS} >> analysis/analysis.txt 
	cd ../
done	


for result in `ls`; do
	max_score=`grep "max" $result/analysis/analysis.txt | awk '{print $2}'`
	mean_score=`grep "mean" $result/analysis/analysis.txt | awk '{print $2}'`
	std_score=`grep "std" $result/analysis/analysis.txt | awk '{print $2}'`
	best_sol=`grep "Best" $result/analysis/analysis.txt | awk '{print $2}'`
	time_max_score=`grep "time" $result/$best_sol/${best_sol}.txt | awk '{print $2}'`
	mean_time=`grep "mean" $result/analysis/analysis.txt | awk '{print $4}'`
	std_time=`grep "std" $result/analysis/analysis.txt | awk '{print $4}'`
	printf "%s,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n" "$result" "$max_score" "$mean_score" "$std_score" "$time_max_score" "$mean_time" "$std_time" >> all_results.csv
done

sort -t',' -k2,2 -n -r all_results.csv > all_results_sorted_by_max_score.csv

file_csv="all_results_sorted_by_max_score.csv"
headline="configuration,max_score,mean_score,std_score,time_max_score,mean_time,std_time"
echo "$headline" > tmpfile
cat "$file_csv" >> tmpfile
mv tmpfile "$file_csv"

