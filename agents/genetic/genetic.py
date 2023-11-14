import sys
from os import path
sys.path.append( path.dirname(path.dirname( path.dirname( path.abspath(__file__) ) ) ))

import random
import numpy as np
import copy
import argparse
from env.network_security_game import NetworkSecurityEnvironment
from agents.random.random_agent import RandomAgent
from env.game_components import Action, ActionType #, IP, Data, Network, Service
 
def individual_init(env, args, size):
    observation = env.reset()
    individual = []
    random_agent = RandomAgent(env,args)
    for i in range(size):
        new_action = random_agent.move(observation, individual)
        individual.append(new_action)
        observation = env.step(new_action)
    return individual


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


def mutation_operator(individual, env, index):
    observation = env.reset()
    new_action = []
    for i in range(len(individual)):
        if i < index:
            valid_actions = generate_valid_actions(observation.state)
            if individual[i] in valid_actions:
                observation = env.step(individual[i])
            else:
                index = i
        else:
            break
    valid_actions = generate_valid_actions(observation.state)
    new_action.append(random.choice(valid_actions))
    return individual[:index] + new_action + individual[index+1:]


def fitness_eval_ra(individual, env): #action_id, new_observation, x, goal, pre_validate, index):
    observation = env.reset()
    goal = copy.deepcopy(env._win_conditions)
    reward = 0
    for i in range(len(individual)):
        previous_state = observation.state
        valid_actions = generate_valid_actions(previous_state)
        if individual[i] in valid_actions:
            observation = env.step(individual[i])
            current_state = observation.state
            if current_state != previous_state:
                reward += observation.reward * (-10) 
            else:
                reward += 0
        else:
            reward += observation.reward * 100
        if observation.done:
            reward += observation.reward * (-10000)
            break
    final_reward = reward * i 
    return final_reward

    
env = NetworkSecurityEnvironment("netsecenv-task.yaml")
parser = argparse.ArgumentParser()
parser.add_argument("--force_ignore", help="Force ignore repeated actions in code", default=False, action=argparse.BooleanOptionalAction)
args = parser.parse_args()

max_number_steps = 20

# GA parameters
population_size = 100
num_generations = 100
mutation_prob = 0.1

# Iinitialize population
population = [individual_init(env,args,20) for _ in range(population_size)]

# Generations
for generation in range(num_generations):
    # Evaluar la aptitud de cada individuo en la población
    scores = [fitness_eval_ra(individual, env) for individual in population]
    # Seleccionar a los mejores individuos
    best_indices = np.argsort(scores)[-population_size:]
    population = [population[i] for i in best_indices]
    # Cruzar a los individuos para crear una nueva generación
    new_generation = []
    while len(new_generation) < population_size:
        father = random.choice(population)
        mother = random.choice(population)
        cross_point = random.randint(1, max_number_steps - 1)
        son = father[:cross_point] + mother[cross_point:]
        new_generation.append(son)
    population = new_generation
    # Aplicar mutaciones
    for i in range(population_size):
        if random.random() < mutation_prob:
            mutation_index = random.randint(0, max_number_steps - 1)
            population[i] = mutation_operator(population[i], env, mutation_index)

# Encontrar la mejor secuencia
best_sequence = max(population, key=lambda x:fitness_eval_ra(x,env))
best_score = fitness_eval_ra(best_sequence,env)

print("Mejor secuencia encontrada:", best_sequence)
print("Puntuación de la mejor secuencia:", best_score)

final_scores = [fitness_eval_ra(individual, env) for individual in population]

