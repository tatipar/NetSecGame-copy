import random
import json

import copy
import argparse
from env.network_security_game import NetworkSecurityEnvironment
from env.game_components import ActionType, Action, IP, Data, Network, Service
from agents.random.random_agent import RandomAgent

env = NetworkSecurityEnvironment("netsecenv-task.yaml")
observation = env.reset()


def action_map(action_id):
    map_dic = {
        0: ActionType.ScanNetwork,
        1: ActionType.FindServices,
        2: ActionType.FindData,
        3: ActionType.ExploitService,
        4: ActionType.ExfiltrateData#,
        #5: ActionType.NoAction
    }    
    # Verificar si el número está en el diccionario y devolver la cadena correspondiente
    try: 
        return map_dic[action_id]
    except ValueError:
        print("No valid entry.")


def pre_validate_action(action_id, state):
    valid = False
    try:
        action_str = action_map(action_id).name
        match action_str:
            case 'ScanNetwork':
                if len(state.known_networks) > 0:
                    valid = True       
            case 'FindServices':
                if len(state.known_hosts) > 0: # and len(set(known_hosts)-set(contr_hosts))>0: ESTO PARA EL FITNESS
                    valid = True
            case 'ExploitService':
                if len(state.known_services) > 0:
                    valid = True
            case 'FindData':
                if len(state.controlled_hosts) > 0:
                    valid = True
            case 'ExfiltrateData':
                if len(state.known_data) > 0:
                    valid = True
            case _:
                valid = False
        return valid
    except:
        return False
        
        
def choose_parameters(action_info, state, goal):
    json_data = json.loads(state.as_json())
    
    known_nets = json_data["known_networks"]
    known_hosts = json_data["known_hosts"]
    contr_hosts = json_data["controlled_hosts"]
    known_serv = json_data["known_services"]
    known_data = json_data["known_data"]
    
    x = False
    action_type = action_map(int(action_info["id"]))
    match action_type.name:
        case 'ScanNetwork':
            network = random.choice(known_nets)
            parameters = {"target_network": Network(IP(network["ip"]), network["mask"])}
        case 'FindServices':
            host = random.choice(known_hosts)
            parameters = {"target_host": IP(host["ip"])}
            if host in contr_hosts:
                x = True
        case 'ExploitService':
            host = random.choice(list(known_serv))
            service = random.choice(known_serv[host])
            parameters = {"target_host": IP(host), "target_service": Service(service["name"], service["type"], service["version"], service["is_local"])}
            if host in contr_hosts:
                x = True
        case 'FindData':
            host = random.choice(contr_hosts)
            parameters = {"target_host": IP(host)}
        case 'ExfiltrateData':
            target_host = list(goal["known_data"].keys())[0]
            source_host = random.choice(list(known_data))
            data_choose = random.choice(source_host)
            parameters = {"target_host": IP(target_host), "source_host": IP(source_host), "data": Data(data_choose["owner"], data_choose["id"])}
            if (source_host == target_host) or (data_choose in known_data[target_host]):
                x = True
    #new_action = Action(action_type=action_type, params=parameters)
    action_info["parameters"] = parameters
    action_info["redundant"] = x
    return action_info #new_action, x
        # METER x EN action_info ??
        


def fitness_eval(individual, env, goal): #action_id, new_observation, x, goal, pre_validate, index):
    observation = env.reset()
    reward = 0
    for i in range(len(individual)):
        current_state = observation.state
        if len(individual[i]) == 1:
            pre_validate = pre_validate_action(int(individual[i]["id"]), current_state)
            if pre_validate:
                individual[i] = choose_parameters(individual[i], current_state, goal)
            else:
                reward += # PENALIZAR
                break
        action_type = action_map(int(action_info["id"]))
        parameters = action_info["parameters"]
        redundant = action_info["redundant"]
        observation = env.step(Action(action_type=action_type, params=parameters))
        if redundant:
            reward += observation.reward # * FACTOR ?? Caso negativo: hizo una elección que no aporta, como explotar un servicio que ya había explotado antes
        else:
            reward += observation.reward # * FACTOR ?? Caso positivo: eligió bien los parámetros
        if observation.done:
            reward += observation.reward # * FACTOR ?? GRAN recompensa por alcanzar el objetivo
            break
    final_reward = reward # * i * FACTOR proporcional (o inversamente proporcional) a la posición dentro del vector
    return individual, final_reward
    

