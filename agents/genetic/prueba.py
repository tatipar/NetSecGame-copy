import random
import json

import copy
import argparse
from env.network_security_game import NetworkSecurityEnvironment
from env.game_components import ActionType, Action, IP, Data, Network, Service
from agents.random.random_agent import RandomAgent

env = NetworkSecurityEnvironment("netsecenv-task.yaml")
observation = env.reset()
new_observation=env.step(Action(ActionType.FindServices,params={"target_host":IP("192.168.1.2")}))
new_observation=env.step(Action(ActionType.ExploitService,params={"target_host":IP("192.168.1.2"),"target_service":Service(name='lanman server', type='passive', version='10.0.19041', is_local=False)}))
new_observation=env.step(Action(ActionType.FindData,params={"target_host":IP("192.168.1.2")}))
new_observation=env.step(Action(ActionType.ExfiltrateData,params={"target_host":IP("213.47.23.195"),"source_host":IP("192.168.1.2"),"data":Data(owner='User1', id='DataFromServer1')}))

json_data = json.loads(observation.state.as_json())
ip12=list(json_data["known_services"].keys())[0]
env.step(Action(ActionType.ExploitService,params={"target_host":IP(ip12), "target_service":Service(name=json_data["known_services"][ip12][0]["name"], type=json_data["known_services"][ip12][0]["type"], version=json_data["known_services"][ip12][0]["version"], is_local=json_data["known_services"][ip12][0]["is_local"])}))


