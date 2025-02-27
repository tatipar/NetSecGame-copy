# # Authors:  Ondrej Lukas - ondrej.lukas@aic.fel.cvut.cz
# #           Arti
# from network_security_game import Network_Security_Environment
# #from environment import *
# from game_components import *
# import numpy as np
# from random import random
# import argparse
# import logging
# #from torch.utils.tensorboard import SummaryWriter
# from scenarios import scenario_configuration, smaller_scenario_configuration, tiny_scenario_configuration

# import tensorflow_gnn as tfgnn
# import tensorflow as tf
# #import tensorflow_probability as tfp

# tf.get_logger().setLevel('ERROR')


# class GNN_REINFORCE_Agent:
#     """
#     Class implementing the REINFORCE algorithm with GNN as input layer
#     """

#     def __init__(self, env:Network_Security_Environment, args: argparse.Namespace):

#         self.env = env
#         self.args = args
#         self._transition_mapping = [k for k in transitions.keys()]
#         graph_schema = tfgnn.read_schema("schema.pbtxt")
#         self._example_input_spec = tfgnn.create_graph_spec_from_schema_pb(graph_schema)

#         #model building blocks
#         def set_initial_node_state(node_set, node_set_name):
#             d1 = tf.keras.layers.Dense(32,activation="relu")(node_set['node_type'])
#             return tf.keras.layers.Dense(32,activation="relu")(d1)


#         def dense_layer(units=32,l2_reg=0.1,dropout=0.25,activation='relu'):
#             regularizer = tf.keras.regularizers.l2(l2_reg)
#             return tf.keras.Sequential([tf.keras.layers.Dense(units, activation=activation, kernel_regularizer=regularizer, bias_regularizer=regularizer),  tf.keras.layers.Dropout(dropout)])

#         #input
#         input_graph = tf.keras.layers.Input(type_spec=self._example_input_spec, name="actor_input")
#         #process node features with FC layer
#         graph = tfgnn.keras.layers.MapFeatures(node_sets_fn=set_initial_node_state, name="actor_preprocess")(input_graph)

#         #Graph conv
#         graph_updates = 4 # TODO Add to args
#         for i in range(graph_updates):
#             graph = tfgnn.keras.layers.GraphUpdate(
#                 node_sets = {
#                     'nodes': tfgnn.keras.layers.NodeSetUpdate({
#                         'related_to': tfgnn.keras.layers.SimpleConv(
#                             message_fn = dense_layer(units=128), #TODO add num_units to args
#                             reduce_type="sum",
#                             receiver_tag=tfgnn.TARGET)},
#                         tfgnn.keras.layers.NextStateFromConcat(dense_layer(32)))}, name=f"actor_graph_update_{i}")(graph)  #TODO add num_units to args

#         node_embeddings = tfgnn.keras.layers.Readout(node_set_name="nodes"  )(graph)
#         # Pool to get a single vector representing the graph
#         pooling = tfgnn.keras.layers.Pool(tfgnn.CONTEXT, "max",node_set_name="nodes", name="actor_pooling")(graph)
#         # Two hidden layers (Followin the REINFORCE)
#         hidden1 = tf.keras.layers.Dense(64, activation="relu", name="actor_fc1")(pooling)
#         hidden2 = tf.keras.layers.Dense(32, activation="relu", name="actor_fc2")(hidden1)

#         # Output layer
#         action_logits  = tf.keras.layers.Dense(5, activation=None, name="actor_action_logits")(hidden2)

#         #sample action
#         #sampled_action = tfp.distributions.RelaxedOneHotCategorical(args.gs_temparature, logits=action_logits)

#         sampled_action = action_logits
#         g_action = tf.keras.layers.Concatenate()([sampled_action, pooling])

#         #action_embedding
#         action_embedding = tf.keras.layers.Dense(32,activation="relu")(g_action)

#         #p1 attention
#         p1_arg, p1_attention_weights = tf.keras.layers.Attention()([action_embedding,node_embeddings],return_attention_scores=True)

#         g_a_p1 = tf.keras.layers.Concatenate()([pooling, sampled_action, p1_arg])
#         g_a_p1_emb = tf.keras.layers.Dense(32,activation="relu")(g_a_p1)

#         #p2 attention
#         p2_arg, p2_attention_weights = tf.keras.layers.Attention()([g_a_p1_emb,node_embeddings],return_attention_scores=True)
#         g_a_p2 = tf.keras.layers.Concatenate()([pooling, sampled_action, p2_arg])
#         g_a_p2_emb = tf.keras.layers.Dense(32,activation="relu")(g_a_p2)

#         #p3 attention
#         _, p3_attention_weights = tf.keras.layers.Attention()([g_a_p2_emb,node_embeddings],return_attention_scores=True)


#         #Build the model
#         self._model = tf.keras.Model(input_graph, [action_logits, p1_attention_weights, p2_attention_weights, p3_attention_weights], name="Actor")


#         self._model.compile(tf.keras.optimizers.Adam(learning_rate=args.lr, clipvalue=5.0))


#         # #baseline
#         # #input
#         # input_graph = tf.keras.layers.Input(type_spec=self._example_input_spec)
#         # #process node features with FC layer
#         # graph = tfgnn.keras.layers.MapFeatures(node_sets_fn=set_initial_node_state,)(input_graph)

#         # #Graph conv
#         # graph_updates = 3 # TODO Add to args
#         # for i in range(graph_updates):
#         #     graph = tfgnn.keras.layers.GraphUpdate(
#         #         node_sets = {
#         #             'nodes': tfgnn.keras.layers.NodeSetUpdate({
#         #                 'related_to': tfgnn.keras.layers.SimpleConv(
#         #                     message_fn = dense_layer(units=128), #TODO add num_units to args
#         #                     reduce_type="max",
#         #                     receiver_tag=tfgnn.TARGET)},
#         #                 tfgnn.keras.layers.NextStateFromConcat(dense_layer(64)))}, name=f"graph_update_{i}")(graph)  #TODO add num_units to args
#         # # Pool to get a single vector representing the graph
#         # pooling = tfgnn.keras.layers.Pool(tfgnn.CONTEXT, "mean",node_set_name="nodes")(graph)
#         # # Two hidden layers (Followin the REINFORCE)
#         # hidden2 = tf.keras.layers.Dense(64, activation="relu", name="baseline_hidden")(pooling)

#         # # Output layer
#         # out_baseline  = tf.keras.layers.Dense(1, activation=None, name="baseline_value")(hidden2)

#         # #Build the model
#         # self._baseline = tf.keras.Model(input_graph, out_baseline, name="Baseline model")
#         # self._baseline.compile(tf.keras.optimizers.Adam(learning_rate=args.lr), loss=tf.losses.MeanSquaredError())





#         self._model.summary()
#         #self._baseline.summary()
#     def _create_graph_tensor(self, node_features, controlled, edges):
#         src,trg = [x[0] for x in edges],[x[1] for x in edges]


#         node_f =  np.hstack([np.array(np.eye(6)[node_features], dtype='int32'), np.array([controlled], dtype='int32').T])
#         graph_tensor =  tfgnn.GraphTensor.from_pieces(
#             node_sets = {"nodes":tfgnn.NodeSet.from_fields(

#                 sizes = [len(node_features)],
#                 features = {"node_type":node_f} # one-hot encoded node features TODO remove hardcoded max value
#             )},
#             edge_sets = {
#                 "related_to": tfgnn.EdgeSet.from_fields(
#                 sizes=[len(src)],
#                 features = {},
#                 adjacency=tfgnn.Adjacency.from_indices(
#                 source=("nodes", np.array(src, dtype='int32')),
#                 target=("nodes", np.array(trg, dtype='int32'))))
#             }
#         )
#         return graph_tensor


#         return tf.keras.layers.Dense(32,activation="relu")(node_set['node_type']) #TODO args

#     def _build_batch_graph(self, state_graphs):

#         def _gen_from_list():
#             for g in state_graphs:
#                 yield g
#         ds = tf.data.Dataset.from_generator(_gen_from_list, output_signature=self._example_input_spec)
#         graph_tensor_batch = next(iter(ds.batch(len(state_graphs))))
#         scalar_graph_tensor = graph_tensor_batch.merge_batch_to_components()
#         return scalar_graph_tensor

#     def _get_discounted_rewards(self, rewards:list)->list:
#         returns = np.array([self.args.gamma ** i * rewards[i] for i in range(len(rewards))])
#         returns =  np.flip(np.cumsum(np.flip(returns)))
#         return returns.tolist()

#     @tf.function
#     def predict(self, state_graph, training=False):
#         return self._model(state_graph, training=training)

#     #@tf.function
#     def _make_training_step_actor(self, inputs, labels, weights)->None:
#         #perform training step
#         with tf.GradientTape() as tape:
#             logits = self.predict(inputs, training=True)
#             cce = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
#             loss = cce(labels, logits, sample_weight=weights)
#         grads = tape.gradient(loss, self._model.trainable_weights)
#         self._model.optimizer.apply_gradients(zip(grads, self._model.trainable_weights))
#         del logits

#     def _make_training_step_baseline(self, inputs, rewards)->None:
#         #perform training step
#         with tf.GradientTape() as tape:
#             values = self._baseline(inputs, training=True)
#             loss = self._baseline.loss(values, rewards)
#         grads = tape.gradient(loss, self._baseline.trainable_weights)
#         self._baseline.optimizer.apply_gradients(zip(grads, self._baseline.trainable_weights))

#     def _preprocess_inputs(self, replay_buffer):
#         raise NotImplementedError

#     def save_model(self, filename):
#         raise NotImplementedError

#     def load_model(self, filename):
#         raise NotImplementedError

#     def _contruct_action_from_logits(self, logits_a, logits_p1, logits_p2, logits_p3, node_mapping, sample=True)-> Action:
#         if sample:
#             print(len(self._transition_mapping), logits_a.shape)
#             transition_type = self._transition_mapping[random.choices([x for x in range(len(self._transition_mapping))], weights=tf.squeeze(tf.nn.softmax(logits_a)), k=1)[0]]
#             p1 = node_mapping[random.choices([x for x in range(len(node_mapping))], weights=tf.squeeze(tf.nn.softmax(logits_p1)), k=1)[0]]
#             p2 = node_mapping[random.choices([x for x in range(len(node_mapping))], weights=tf.squeeze(tf.nn.softmax(logits_p2)), k=1)[0]]
#             p3 = node_mapping[random.choices([x for x in range(len(node_mapping))], weights=tf.squeeze(tf.nn.softmax(logits_p3)), k=1)[0]]
#         else:
#             transition_type = self._transition_mapping[np.argmax(tf.squeeze(tf.nn.softmax(logits_a)))]
#             p1 = node_mapping[np.argmax(tf.squeeze(tf.nn.softmax(logits_p1)))]
#             p2 = node_mapping[np.argmax(tf.squeeze(tf.nn.softmax(logits_p2)))]
#             p3 = node_mapping[np.argmax(tf.squeeze(tf.nn.softmax(logits_p3)))]
#         return self._build_action(transition_type, p1, p2,p3)


#     def _build_action(self, transition, p1, p2,p3)->Action:
#         if transition == "ScanNetwork":
#             return Action(transition, {"target_network": p1})
#         elif transition == "FindServices":
#             return Action(transition, {"target_host": p1})
#         elif transition == "FindData":
#             return Action(transition, {"target_host": p1})
#         elif transition == "ExecuteCodeInService":
#             return Action(transition, {"target_host": p1, "target_service":p2})
#         elif transition == "ExfiltrateData":
#             return Action(transition, {"target_host": p1, "source_host":p2, "data": p3})
#         else:
#             return None



#     #@profile
#     def train(self):
#         for episode in range(self.args.episodes):
#             #collect data
#             batch_states, batch_actions, batch_returns = [], [], []
#             while len(batch_states) < args.batch_size:
#                 #perform episode
#                 states, actions, rewards = [], [], []
#                 state, done = env.reset().observation, False

#                 while not done:
#                     state_node_f,controlled, state_edges = state.as_graph
#                     state_g = self._create_graph_tensor(state_node_f, controlled, state_edges)
#                     #predict action probabilities
#                     probabilities = self.predict(state_g)
#                     probabilities = tf.squeeze(tf.nn.softmax(probabilities))

#                     action = random.choices([x for x in range(len(self._transition_mapping))], weights=probabilities, k=1)[0]
#                     #select action and perform it
#                     next_state = self.env.step(self._transition_mapping[action])


#                     #print(self._transition_mapping[action])
#                     states.append(state_g)
#                     actions.append(action)
#                     rewards.append(next_state.reward)

#                     #move to the next state
#                     state = next_state.observation
#                     done = next_state.done

#                 discounted_returns = self._get_discounted_rewards(rewards)

#                 batch_states += states
#                 batch_actions += actions
#                 batch_returns += discounted_returns


#             #shift batch_returns to non-negative
#             #batch_returns = batch_returns + np.abs(np.min(batch_returns)) + 1e-10

#             #OLDER VERSION OF DATASET BUILIDING
#             # with tf.io.TFRecordWriter("tmp_record_file") as writer:
#             #     for graph in batch_states:
#             #         example = tfgnn.write_example(graph)
#             #         writer.write(example.SerializeToString())

#             # #Create TF dataset
#             # dataset = tf.data.TFRecordDataset("tmp_record_file")
#             # #de-serialize records
#             # new_dataset = dataset.map(lambda serialized: tfgnn.parse_single_example(serialized=serialized, spec=self._example_input_spec))
#             # # #get batch of proper size
#             # batch_data = new_dataset.batch(len(batch_states))
#             # graph_tensor_batch = next(iter(batch_data))

#             # #convert batch into scalar graph with multiple components
#             # scalar_graph_tensor = graph_tensor_batch.merge_batch_to_components()


#             batch_returns = np.array(batch_returns)

#             scalar_graph_tensor = self._build_batch_graph(batch_states)
#             #perform training step
#             baseline = tf.squeeze(self._baseline(scalar_graph_tensor))
#             self._make_training_step_baseline(scalar_graph_tensor, batch_returns)
#             updated_batch_returns = batch_returns-baseline
#             self._make_training_step_actor(scalar_graph_tensor, batch_actions, updated_batch_returns)



#             #evaluate
#             if episode > 0 and episode % args.eval_each == 0:
#                 returns = []
#                 for _ in range(self.args.eval_for):
#                     state, done = env.reset().observation, False
#                     ret = 0
#                     #print("--------------")
#                     while not done:
#                         state_node_f,controlled, state_edges = state.as_graph
#                         state_g = self._create_graph_tensor(state_node_f,controlled,state_edges)
#                         #predict action probabilities
#                         a_logits, p1_logits, p2_logits, p3_logits = self.predict(state_g)


#                         action = self._transition_mapping[np.argmax(tf.squeeze(tf.nn.softmax(a_logits)))]
#                         # p1 = node_mapping[np.argmax(tf.squeeze(tf.nn.softmax(p1_logits)))]
#                         # p2 = node_mapping[np.argmax(tf.squeeze(tf.nn.softmax(p2_logits)))]
#                         # p3 = node_mapping[np.argmax(tf.squeeze(tf.nn.softmax(p3_logits)))]


#                         next_state = self.env.step(action)
#                         ret += next_state.reward
#                         state = next_state.observation
#                         done = next_state.done

#                     returns.append(ret)
#                 print(f"Evaluation after {episode} episodes (mean of {len(returns)} runs): {np.mean(returns)}+-{np.std(returns)}")
#             else:
#                 pass
#                 #print(f"Episode {episode} done.")

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()

#     #env arguments
#     parser.add_argument("--max_steps", help="Sets maximum steps before timeout", default=7, type=int)
#     parser.add_argument("--defender", help="Is defender present", default=False, action="store_true")
#     parser.add_argument("--scenario", help="Which scenario to run in", default="scenario1", type=str)
#     parser.add_argument("--random_start", help="Sets evaluation length", default=False, action="store_true")
#     parser.add_argument("--verbosity", help="Sets verbosity of the environment", default=0, type=int)

#     #model arguments
#     parser.add_argument("--episodes", help="Sets number of training episodes", default=2000, type=int)
#     parser.add_argument("--gamma", help="Sets gamma for discounting", default=0.99, type=float)
#     parser.add_argument("--batch_size", help="Batch size for NN training", type=int, default=32)
#     parser.add_argument("--lr", help="Learnining rate of the NN", type=float, default=1e-3)
#     parser.add_argument("--gs_temparature", help="Temperature for gumball softmax", type=float, default=0.5)

#     #training arguments
#     parser.add_argument("--eval_each", help="During training, evaluate every this amount of episodes.", default=200, type=int)
#     parser.add_argument("--eval_for", help="Sets evaluation length", default=100, type=int)

#     parser.add_argument("--test", help="Do not train, only run test", default=False, action="store_true")
#     parser.add_argument("--test_for", help="Sets evaluation length", default=1000, type=int)


#     parser.add_argument("--seed", help="Sets the random seed", type=int, default=42)

#     args = parser.parse_args()
#     args.filename = "GNN_Reinforce_Agent_" + ",".join(("{}={}".format(key, value) for key, value in sorted(vars(args).items()) if key not in ["evaluate", "eval_each", "eval_for"])) + ".pickle"

#     logging.basicConfig(filename='GNN_Reinforce_Agent.log', filemode='a', format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',level=logging.INFO)
#     logger = logging.getLogger('GNN_Reinforce_Agent')

#     # Setup tensorboard
#     # run_name = f"netsecgame__GNN_Reinforce__{args.seed}__{int(time.time())}"
#     # writer = SummaryWriter(f"logs/{run_name}")
#     # writer.add_text(
#     #     "hypherparameters",
#     #     "|param|value|\n|-|-|\n%s" % ("\n".join([f"|{key}|{value}|" for key, value in vars(args).items()]))
#     # )

#     #set random seed
#     np.random.seed(args.seed)
#     tf.random.set_seed(args.seed)
#     random.seed(args.seed)
#     logger.info(f'Setting the network security environment')
#     env = Network_Security_Environment(random_start=args.random_start, verbosity=args.verbosity)
#     if args.scenario == "scenario1":
#         env.process_cyst_config(scenario_configuration.configuration_objects)
#     elif args.scenario == "scenario1_small":
#         env.process_cyst_config(smaller_scenario_configuration.configuration_objects)
#     elif args.scenario == "scenario1_tiny":
#         env.process_cyst_config(tiny_scenario_configuration.configuration_objects)
#     else:
#         print("unknown scenario")
#         exit(1)

#     # define attacker goal and initial location
#     if args.random_start:
#         goal = {
#             "known_networks":set(),
#             "known_hosts":set(),
#             "controlled_hosts":set(),
#             "known_services":{},
#             "known_data":{"213.47.23.195":"random"}
#         }
#         attacker_start = {
#             "known_networks":set(),
#             "known_hosts":set(),
#             "controlled_hosts":{"213.47.23.195","192.168.2.0/24"},
#             "known_services":{},
#             "known_data":{}
#         }
#     else:
#         goal = {
#             "known_networks":set(),
#             "known_hosts":{},
#             "controlled_hosts":{"192.168.1.2"},
#             "known_services":{},
#             "known_data":{}     #"213.47.23.195":{("User1", "DataFromServer1")}
#         }

#         attacker_start = {
#             "known_networks":set(),
#             "known_hosts":set(),
#             "controlled_hosts":{"213.47.23.195","192.168.2.2"},
#             "known_services":{},
#             "known_data":{}
#         }

#     # Training
#     logger.info(f'Initializing the environment')
#     state = env.initialize(win_conditions=goal, defender_positions=args.defender, attacker_start_position=attacker_start, max_steps=args.max_steps)
#     logger.info(f'Creating the agent')
#     # #initialize agent
#     agent = GNN_REINFORCE_Agent(env, args)
#     state, done = env.reset().observation, False
#     state_node_f,controlled, state_edges, node_mapping = state.as_graph
#     state_g = agent._create_graph_tensor(state_node_f, controlled, state_edges)

#     a_logits, p1_logits, p2_logits, p3_logits = agent.predict(state_g)

#     print(state)
#     a = agent._contruct_action_from_logits(a_logits, p1_logits, p2_logits, p3_logits,node_mapping,sample=False)
#     a_s = agent._contruct_action_from_logits(a_logits, p1_logits, p2_logits, p3_logits,node_mapping,sample=True)
#     print(f"Playing {a}, sampled{a_s}")
#     next_state = env.step(a)
#     print(next_state.observation, next_state.reward )
