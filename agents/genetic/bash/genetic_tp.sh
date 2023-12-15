#!/bin/bash

PATH_REPO=`git rev-parse --show-toplevel` # show the path of the top-level directory

# population and generations parameters
POPULATION_SIZE=100
NUM_GENERATIONS=500

# parents selection parameters
TOURNAMENT=false # if true: tournament selection, else: roulette wheel selection
REPLACEMENT=true # if true: parents selection with replacement, else: without replacement
NUM_PER_TOURNAMENT=4

# crossover parameters
N_POINTS=false # if true: N-points crossover, else: uniform crossover
NUM_POINTS=3
CROSS_PROB=0.8
P_VALUE=0.5

# mutation parameters
PARAMETER_MUTATION=true # if true: mutation by parameter, else: mutation by action
MUTATION_PROB=0.1

# survivor selection parameters
STEADY_STATE=true # if true: steady-state selection, else: random selection
NUM_REPLACE=30


# set names for directory
if ${TOURNAMENT}; then
	var1="tournament";
else
	var1="rouletteWheel"
fi

if ${N_POINTS}; then
	var2="Npoints";
else
	var2="uniform"
fi

if ${PARAMETER_MUTATION}; then
	var3="parameter";
else
	var3="action"
fi

if ${STEADY_STATE}; then
	var4="steadyState";
else
	var4="random"
fi


# run experiment

PATH_GENETIC="${PATH_REPO}/agents/genetic"

PROCESS_ID=$$
TIME_MARK=$(date +%s)

PATH_RESULTS="${PATH_GENETIC}/results/${var1}_${var2}_${var3}_${var4}/results_${PROCESS_ID}_${TIME_MARK}"

mkdir -p ${PATH_RESULTS}

cd ${PATH_RESULTS}

python3 -u ${PATH_GENETIC}/python/genetic_tp.py ${POPULATION_SIZE} ${NUM_GENERATIONS} ${TOURNAMENT} ${REPLACEMENT} ${NUM_PER_TOURNAMENT} ${N_POINTS} ${NUM_POINTS} ${CROSS_PROB} ${P_VALUE} ${PARAMETER_MUTATION} ${MUTATION_PROB} ${STEADY_STATE} ${NUM_REPLACE} ${PATH_GENETIC} ${PATH_RESULTS} >> results_${PROCESS_ID}_${TIME_MARK}.txt 2>&1


