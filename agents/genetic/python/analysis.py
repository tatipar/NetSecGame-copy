import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import path
import sys

PATH_RESULTS = str(sys.argv[1])


## Analysis over ten repetitions ##

score_last_generation = pd.read_csv(path.join(PATH_RESULTS, "analysis_20rep/best_score_last_generation"), names=["best_score"])
generations = pd.read_csv(path.join(PATH_RESULTS, "analysis_20rep/number_generations"), names=["generations"])
time =  pd.read_csv(path.join(PATH_RESULTS, "analysis_20rep/total_time"), names=["time"])


fig, ax1 = plt.subplots()
box1 = ax1.boxplot(score_last_generation, positions=[1], vert=True, widths=0.6, patch_artist=True, medianprops={'color': 'b'}, labels=["Score"])
_ = ax1.set_ylabel('Fitness value best solution', color='b')
_ = ax1.tick_params('y', colors='b')

ax2 = ax1.twinx()
box2 = ax2.boxplot(time, positions=[2], vert=True, widths=0.6, patch_artist=True, medianprops={'color': 'darkred'}, labels=["Time"])
_ = ax2.set_ylabel('Time [$s$]', color='r')
_ = ax2.tick_params('y', colors='r')

colors = ['lightblue', 'lightcoral']
for bplot, color in zip([box1, box2], colors):
    for patch in bplot['boxes']:
        patch.set_facecolor(color)

plt.suptitle("Metrics over twenty repetitions")
_ = plt.savefig(path.join(PATH_RESULTS, "analysis_20rep/boxplot_20results.png"))


df = pd.concat([score_last_generation, generations, time], axis=1)
print("\n", df.describe())


## Analysis over best repetition ##

best = np.argmax(score_last_generation)
if best <= 9:
    best_string = "0" + str(best)
else:
    best_string = str(best)
print("\nBest: results_", best_string, "\n",  sep='')

best_solution_max_scores = pd.read_csv(path.join(PATH_RESULTS, f'results_{best_string}/best_scores.csv'), names=["score", "good_actions", "boring_actions", "bad_actions", "num_steps"])
best_solution_mean_scores = pd.read_csv(path.join(PATH_RESULTS, f'results_{best_string}/metrics_mean.csv'), names=["score", "good_actions", "boring_actions", "bad_actions", "num_steps"])
best_solution_std_scores = pd.read_csv(path.join(PATH_RESULTS, f'results_{best_string}/metrics_std.csv'), names=["score", "good_actions", "boring_actions", "bad_actions", "num_steps"])

num_generations = len(best_solution_max_scores)

fig = plt.figure()
_ = plt.plot(np.arange(num_generations), best_solution_mean_scores.iloc[:,0], label='mean')
_ = plt.plot(np.arange(num_generations), best_solution_max_scores.iloc[:,0], label='max')
_ = plt.plot(np.arange(num_generations), best_solution_std_scores.iloc[:,0], label='std')
_ = plt.legend()
_ = plt.xlabel("Generation")
_ = plt.ylabel("Fitness value")
_ = plt.title("Scores over each generation - Best repetition")
_ = plt.savefig(path.join(PATH_RESULTS, "analysis_20rep/scores.png"))


fig = plt.figure()
_ = plt.boxplot(best_solution_max_scores.iloc[:,0], labels=['Score'])
_ = plt.ylabel("Fitness value")
_ = plt.title("Maximum score over each generation - Best repetition")
_ = plt.savefig(path.join(PATH_RESULTS, "analysis_20rep/best_solution_boxplot_score.png"))


fig = plt.figure()
_ = plt.boxplot(best_solution_max_scores.iloc[:,1:], labels=['Good', 'Boring', 'Bad', 'Total'])
_ = plt.xlabel("Actions")
_ = plt.ylabel("Quantity")
_ = plt.title("Number of actions - Best repetition")
_ = plt.savefig(path.join(PATH_RESULTS, "analysis_20rep/best_solution_boxplot_actions.png")) 

