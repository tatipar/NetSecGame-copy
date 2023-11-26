import sys
from os import path
# script:
sys.path.append( path.dirname(path.dirname( path.dirname( path.abspath(__file__) ) ) ))
# terminal:
#sys.path.append(path.dirname(path.dirname(path.abspath(''))))

import random
import numpy as np
import copy
#import argparse
from env.network_security_game import NetworkSecurityEnvironment
#from agents.random.random_agent import RandomAgent
from env.game_components import Action, ActionType #, IP, Data, Network, Service


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


def mutation_operator_by_parameter(individual, all_actions_by_type, mutation_prob):
    new_individual = []
    for i in range(len(individual)):
        if random.random() < mutation_prob:
            action_type = individual[i].type
            new_individual.append(random.choice(all_actions_by_type[str(action_type)]))
        else:
            new_individual.append(individual[i])
    return new_individual


def mutation_operator_by_action(individual, all_actions, mutation_prob):
    new_individual = []
    for i in range(len(individual)):
        if random.random() < mutation_prob:
            new_individual.append(random.choice(all_actions))
        else: 
            new_individual.append(individual[i])
    return new_individual


def crossover_operator(parent1, parent2, num_points, cross_prob):
    if random.random() < cross_prob:
        len_ind = len(parent1)
        cross_points = np.sort(np.random.choice(len_ind, num_points, replace=False))
        child1 = []
        child2 = []
        current_parent1 = parent1
        current_parent2 = parent2
        for i in range(len_ind):
            child1.append(current_parent1[i])
            child2.append(current_parent2[i])
            if i in cross_points:
                current_parent1 = parent2 if current_parent1 is parent1 else parent1
                current_parent2 = parent1 if current_parent2 is parent2 else parent2
    else:
        child1 = parent1.copy()
        child2 = parent2.copy()
    return child1, child2


def fitness_eval(individual, observation, goal): 
    num_good_actions = 0
    reward = 0
    current_state = observation.state
    for i in range(len(individual)):
        valid_actions = generate_valid_actions(current_state)
        observation = env.step(individual[i])
        new_state = observation.state
        if individual[i] in valid_actions:
            if current_state != new_state:
                num_good_actions += 1
                reward += 10
            else: reward += 0
        else:
            reward += -100
        current_state = observation.state
    if observation.done:
        reward += 100000
    if num_good_actions > 0:
        return reward * num_good_actions
    else:
        return reward

    
def choose_parents(population, goal, num_per_tournament=2, are_parents_diff=True):
    """ Tournament selection """
    from_population = population.copy()
    chosen = []
    for i in range(2):
        options = []
        for _ in range(num_per_tournament):
            options.append(random.choice(from_population))
        chosen.append(max(options, key=lambda x:fitness_eval(x,env.reset(),goal)))
        if i==0 and are_parents_diff:
            from_population.remove(chosen[0])
    return chosen[0], chosen[1]


def get_all_actions_by_type(all_actions):
    all_actions_by_type = {}
    ScanNetwork_list=[]
    FindServices_list=[]
    ExploitService_list=[]
    FindData_list=[]
    ExfiltrateData_list=[]
    for i in range(len(all_actions)):
        if ActionType.ScanNetwork==all_actions[i].type:
            ScanNetwork_list.append(all_actions[i])
        elif ActionType.FindServices==all_actions[i].type:
            FindServices_list.append(all_actions[i])
        elif ActionType.ExploitService==all_actions[i].type:
            ExploitService_list.append(all_actions[i])
        elif ActionType.FindData==all_actions[i].type:
            FindData_list.append(all_actions[i])
        else:
            ExfiltrateData_list.append(all_actions[i])

    all_actions_by_type["ActionType.ScanNetwork"] = ScanNetwork_list
    all_actions_by_type["ActionType.FindServices"] = FindServices_list
    all_actions_by_type["ActionType.ExploitService"] = ExploitService_list
    all_actions_by_type["ActionType.FindData"] = FindData_list
    all_actions_by_type["ActionType.ExfiltrateData"] = ExfiltrateData_list
    return all_actions_by_type



## The environment is initialized
env = NetworkSecurityEnvironment("netsecenv-task.yaml")

## Info from environment
goal = copy.deepcopy(env._goal_conditions)
max_number_steps = env._max_steps

## Possible actions
all_actions = env.get_all_actions()
all_actions_by_type = get_all_actions_by_type(all_actions)


## GA parameters
population_size = 100
num_generations = 100

# crossover parameters
select_parents_with_replacement = True
num_per_tournament = 2
num_points = 3
cross_prob = 0.8

# mutation parameters
prob_parameter_mutation = 0.5
mutation_prob = 0.1
num_replace = 30


# Initialize population
population = [[random.choice(all_actions) for _ in range(max_number_steps)] for _ in range(population_size)]


# Generations
generation = 0
while (generation < num_generations) or (best_score < 100000):
    print("generation: ",generation)
    generation += 1
    new_generation = []
    offspring = []
    popu_crossover = population.copy()
    for j in range(int(population_size/2)):
        # cross-over
        if j == 0 or select_parents_with_replacement:
            pass
        else:
            popu_crossover.remove(parent1)
            popu_crossover.remove(parent2)
        parent1, parent2 = choose_parents(popu_crossover, goal, num_per_tournament, True)
        child1, child2 = crossover_operator(parent1, parent2, num_points, cross_prob)
        # mutation
        if random.random() < prob_parameter_mutation:
            child1 = mutation_operator_by_parameter(child1, all_actions_by_type, mutation_prob)
            child2 = mutation_operator_by_parameter(child2, all_actions_by_type, mutation_prob)
        else:
            child1 = mutation_operator_by_action(child1, all_actions, mutation_prob)
            child2 = mutation_operator_by_action(child2, all_actions, mutation_prob)
        offspring.append(child1)
        offspring.append(child2)
    # steady-state
    # parents
    parents_scores = [fitness_eval(individual, env.reset(), goal) for individual in population]
    best_indices_parents = np.argsort(parents_scores)[::-1][:population_size]
    parents_sort = [population[i] for i in best_indices_parents]
    parents_scores_sort = [parents_scores[i] for i in best_indices_parents]
    # offspring
    offspring_scores = [fitness_eval(individual, env.reset(), goal) for individual in offspring]
    best_indices_offspring = np.argsort(offspring_scores)[::-1][:population_size]
    offspring_sort = [offspring[i] for i in best_indices_offspring] 
    offspring_scores_sort = [offspring_scores[i] for i in best_indices_offspring] 
    # new generation
    new_generation = parents_sort[:population_size-num_replace] + offspring_sort[:num_replace]
    new_generation_scores = parents_scores_sort[:population_size-num_replace] + offspring_scores_sort[:num_replace]
    best_score = new_generation_scores[0]
    population = new_generation 


# Best sequence
best_sequence = population[0]
best_score = new_generation_scores[0]

print("Best sequence:", best_sequence)
print("Best sequence score:", best_score)

#final_scores = [fitness_eval(individual, env.reset(), goal) for individual in population]

