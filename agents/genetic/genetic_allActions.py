import sys
from os import path
# script:
sys.path.append( path.dirname(path.dirname( path.dirname( path.abspath(__file__) ) ) ))
# terminal:
#sys.path.append(path.dirname(path.dirname(path.abspath(''))))

import random
import numpy as np
import copy
import argparse
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
    """TODO. this function is not complete"""
    which_cross_points = np.sort(np.random.choice(len(parent1), num_points, replace=False)
    son1 = []
    son2 = []
    if random.random() < cross_prob:
        for i in range(len(which_cross_point)):
            son1.append(parent1[:which_cross_point[i]]) + parent2[cross_point:]
        son2 = parent2[:cross_point] + parent1[cross_point:]
    else:
        son1 = parent1.copy()
        son2 = parent2.copy()



def fitness_eval(individual, observation, goal): 
    num_valid_actions = 0
    reward = 1
    for i in range(len(individual)):
        current_state = observation.state
        valid_actions = generate_valid_actions(current_state)
        if individual[i] in valid_actions:
            num_valid_actions += 1
        observation = env.step(individual[i])
        if observation.done:
            reward = 1000 
    return reward * num_valid_actions

    
def choose_parents(population):
    """ Tournament selection """
    options = []
    chosen = []
    for i in range(2):
        options.append(random.choice(population))
        options.append(random.choice(population))
        chosen.append(max(options, key=lambda x:fitness_eval_ra(x,env)))
        options = []
    return chosen[0], chosen[1]


 
env = NetworkSecurityEnvironment("netsecenv-task.yaml")
#observation = env.reset()
parser = argparse.ArgumentParser()
parser.add_argument("--force_ignore", help="Force ignore repeated actions in code", default=False, action=argparse.BooleanOptionalAction)
args = parser.parse_args()
goal = copy.deepcopy(env._win_conditions)

max_number_steps = 20

# GA parameters
population_size = 100
num_generations = 100
mutation_prob = 0.1
cross_prob = 0.8
num_replace = 30

# Initialize population
population = [individual_init(env,args,max_number_steps) for _ in range(population_size)]

# Generations
generation = 0
while (generation < num_generations):# or (best_score < 10000):
    print("generation: ",generation)
    generation += 1
    new_generation = []
    offspring = []
    print(env.timestamp)
    for j in range(int(population_size/2)):
        # cross-over
        parent1, parent2 = choose_parents(population)
        #
        # mutation (one gen):
        #if random.random() < mutation_prob:
        #    mutation_index = random.randint(0, max_number_steps - 1)
        #    son1 = mutation_operator_1gen(son1, env, mutation_index)
        #if random.random() < mutation_prob:
        #    mutation_index = random.randint(0, max_number_steps - 1)
        #    son2 = mutation_operator_1gen(son2, env, mutation_index)
        #
        # mutation (maybe more than one gen):
        son1 = mutation_operator(son1, env, mutation_prob)
        son2 = mutation_operator(son2, env, mutation_prob)
        offspring.append(son1)
        offspring.append(son2)
    # steady-state
    parents_scores = [fitness_eval_ra(individual, env) for individual in population]
    offspring_scores = [fitness_eval_ra(individual, env) for individual in offspring]
    best_indices_parents = np.argsort(parents_scores)[::-1][:population_size]
    parents_sort = [population[i] for i in best_indices_parents]
    best_indices_offspring = np.argsort(offspring_scores)[::-1][:population_size]
    offspring_sort = [offspring[i] for i in best_indices_offspring]
    new_generation = parents_sort[:population_size-num_replace] + offspring_sort[:num_replace]
    population = new_generation
    # Best sequence (in final population)
    best_sequence = max(population, key=lambda x:fitness_eval_ra(x,env))
    best_score = fitness_eval_ra(best_sequence,env)

print("Best sequence:", best_sequence)
print("Best sequence score:", best_score)

#final_scores = [fitness_eval_ra(individual, env) for individual in population]

