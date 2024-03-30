#!/bin/bash

PATH_REPO=`git rev-parse --show-toplevel` # path of the top-level directory

ALL_RESULTS=${PATH_REPO}/agents/genetic/results/results_action
cd ${ALL_RESULTS}

for result in `ls`; do
	cd $result/
	PATH_RESULTS=${ALL_RESULTS}/${result}
	PATH_GENETIC=${PATH_REPO}/agents/genetic/
	python3 -u ${PATH_REPO}/agents/genetic/python/analysis_win.py ${PATH_GENETIC} ${PATH_RESULTS}  
	cd ../
done	


