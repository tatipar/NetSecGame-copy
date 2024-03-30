#!/bin/bash

# Script que automatiza la ejecucion de las diez repeticiones de cada configuracion a probar.



PATH_REPO=`git rev-parse --show-toplevel` # show the path of the top-level directory

# population and generations parameters
POPULATION_SIZE=100
NUM_GENERATIONS=500

# parents selection (tournament) parameters
REPLACEMENT=true
NUM_PER_TOURNAMENT=(5 8)

# crossover parameters
N_POINTS=true # if true: N-points crossover, else: uniform crossover
#NUM_POINTS=(1 3 6)
P_VALUE=0.5
CROSS_PROB=(0.8 1.0)

# mutation parameters
PARAMETER_MUTATION=true # if true: mutation by parameter, else: mutation by action
MUTATION_PROB=(0.0333 0.1)

# survivor selection (steady-state) parameters
NUM_REPLACE=(25 50)


# set names for directory
if ${N_POINTS}; then
	cross_op="Npoints";
	NUM_POINTS=(1 3 6)
else
	cross_op="uniform"
	NUM_POINTS=(999)
fi

if ${PARAMETER_MUTATION}; then
	mut_op="parameter";
else
	mut_op="action"
fi


# run experiment

PATH_GENETIC="${PATH_REPO}/agents/genetic"

for num_per_tournament in "${NUM_PER_TOURNAMENT[@]}"; do
	for cross_prob in "${CROSS_PROB[@]}"; do
		for mut_prob in "${MUTATION_PROB[@]}"; do
			for num_replace in "${NUM_REPLACE[@]}"; do 
				for num_points in "${NUM_POINTS[@]}"; do
					for i in {0..9}; do
						PATH_RESULTS="${PATH_GENETIC}/results/${num_per_tournament}_${cross_op}_${num_points}_${cross_prob}_${mut_op}_${mut_prob}_${num_replace}/results_$(printf "%02d" "$i")"
						mkdir -p ${PATH_RESULTS}
						cd ${PATH_RESULTS}
						python3 -u ${PATH_GENETIC}/python/genetic_tp.py ${POPULATION_SIZE} ${NUM_GENERATIONS} ${REPLACEMENT} ${num_per_tournament} ${N_POINTS} ${num_points} ${P_VALUE} ${cross_prob} ${PARAMETER_MUTATION} ${mut_prob} ${num_replace} ${PATH_GENETIC} ${PATH_RESULTS} >> ${PATH_RESULTS}/results_$(printf "%02d" "$i").txt 2>&1 &
					done
					wait
					cd ${PATH_GENETIC}
				done
			done
		done
	done
done


