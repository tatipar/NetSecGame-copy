import sys
from os import path
sys.path.append( path.dirname(path.dirname( path.dirname(path.dirname( path.abspath(__file__) ) ) )))

import pandas as pd
import numpy as np
import copy
import json
import matplotlib.pyplot as plt

from env.network_security_game import NetworkSecurityEnvironment
from env.game_components import Action, ActionType


PATH_GENETIC = str(sys.argv[1])
PATH_RESULTS = str(sys.argv[2])


def generate_valid_actions(state):
    # (function copied from RandomAgent)
    valid_actions = set()
    #Network Scans
    for network in state.known_networks:
        # TODO ADD neighbouring networks
        valid_actions.add(Action(ActionType.ScanNetwork, params={"target_network": network}))
    # Service Scans
    for host in state.known_hosts:
        valid_actions.add(Action(ActionType.FindServices, params={"target_host": host}))
    # Service Exploits
    for host, service_list in state.known_services.items():
        for service in service_list:
            valid_actions.add(Action(ActionType.ExploitService, params={"target_host": host , "target_service": service}))
    # Data Scans
    for host in state.controlled_hosts:
        valid_actions.add(Action(ActionType.FindData, params={"target_host": host}))
    # Data Exfiltration
    for src_host, data_list in state.known_data.items():
        for data in data_list:
            for trg_host in state.controlled_hosts:
                if trg_host != src_host:
                    valid_actions.add(Action(ActionType.ExfiltrateData, params={"target_host": trg_host, "source_host": src_host, "data": data}))
    return list(valid_actions)


def fitness_eval_v02(individual, observation, goal):
    """ 
    This function rewards when a changing state is observed, it does not care if the action is valid or not (e.g. FindServices on a host before doing the corresponding ScanNetwork is not valid, but it is possible and the state will probably change, so it is rewarded). This kind of action is called "good action".
    Furthermore, if the state does not change but the action is valid, it does not contribute to the reward. This kind of action is called "boring action".
    Actions that do not change the state and are not valid are penalized. This kind of action is called "bad action".
    Finally, the final reward is divided by num_steps - num_good_actions + num_bad_actions.
    """
    i = 0
    num_good_actions = 0
    num_boring_actions = 0
    num_bad_actions = 0
    reward = 0
    reward_goal = 0
    current_state = observation.state
    while i < len(individual) and not observation.done:
        valid_actions = generate_valid_actions(current_state)
        observation = env.step(individual[i])
        new_state = observation.state
        if current_state != new_state:
            reward += 10
            num_good_actions += 1
        else:
            if individual[i] in valid_actions:
                reward += 0
                num_boring_actions += 1
            else:
                reward += -100
                num_bad_actions += 1
        current_state = observation.state
        i += 1
    num_steps = env.timestamp
    if observation.info != {} and observation.info["end_reason"] == "goal_reached":
        reward_goal = 10000
    final_reward = reward + reward_goal
    div_aux = num_steps - num_good_actions + num_bad_actions
    if div_aux == 0:
        # i.e. when num_steps == num_good_actions and num_bad_actions == 0
        # if num_bad_actions > 0, then num_steps + num_bad_actions != num_good_actions because num_steps > num_good_actions
        div = num_steps
    else:
        div = div_aux
    if final_reward >= 0:
        return_reward = final_reward / div
    else:
        return_reward = final_reward 
    return return_reward, num_good_actions, num_boring_actions, num_bad_actions, num_steps, observation


###########################################################################################################################################


env = NetworkSecurityEnvironment(path.join(PATH_GENETIC,"netsecenv-task.yaml"))

## Info from environment
goal = copy.deepcopy(env._goal_conditions)
max_number_steps = env._max_steps

repetition = 20

is_goal = []
for i in range(repetition):
    auxiliar = []
    best_sequence = []
    with open(path.join(PATH_RESULTS,f'results_{i:02}/best_sequence.json'), 'r') as f:
        auxiliar = json.load(f)
    for j in range(max_number_steps):
        best_sequence.append(Action.from_json(auxiliar[j]))
    total_reward, num_good_actions, num_boring_actions, num_bad_actions, num_steps, final_observation = fitness_eval_v02(best_sequence, env.reset(), goal)
    is_goal.append(env.is_goal(final_observation.state))


with open(path.join(PATH_RESULTS,"analysis_20rep/is_goal"), 'w') as f:
    for line in is_goal:
        f.write(str(line) + '\n')


count_true = is_goal.count(True)
count_false = is_goal.count(False)

# Plot histogram
categories = ['Won', 'Lost']
values = [count_true, count_false]

_ = plt.bar(categories, values)
_ = plt.title('Number of times the configuration won or lost')
_ = plt.ylabel('Total number')
_ = plt.grid(axis='y')
plt.savefig(path.join(PATH_RESULTS,"analysis_20rep/histogram_won_lost.png"))

