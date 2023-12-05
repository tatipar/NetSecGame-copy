# Genetic Agent

This agent was trained with a genetic algorithm to solve NSG.

Some considerations:
- There is no defender.
- The execution of actions is deterministic. Actions are executed if the corresponding dependences (defined by NSG) are satisfied.
- When an action can be executed, the state of the environment will probably change. Actions depend on the previous state.
- The set of possible actions that can be tested are called "valid" actions in NSG.
- There are some actions that are "valid" but do not change the state.
- Most "invalid" actions do not change the state, since they can not be executed, but there is associated error. 
- However, there are actions (like FindServices) that can be executed regardless of state (only if the parameter is correct). So, not all "invalid" actions mean that they cannot be executed.

## Modeling

### Objective
The objective is to reach the NSG goal in the fewest number of steps.
The NSG goal is determined in the configurations task file `netsecenv-task.yaml`. It could be modified by the user. Currently it is fixed, but it could be random.

### Population and Individuals
The population representation is a vector, where the i-th element represents the i-th individual in the population.

Each individual is a fixed length vector, representing a sequence of actions as a plan to solve NSG. In the i-th position is the i-th action to try.

Each action consists of an action type (ScanNetwork, FindServices, ExploitService, FindData and ExfiltrateData) and its corresponding parameters.
There is a pool of all possible actions, from which each individual is randomly filled to initialize the population. 

The population has `population_size` individuals, and each individual has `max_number_steps` actions to try.
`population_size` is a hyperparameter that the user should set.
`max_number_steps` depends on the `max_steps` parameter of the configuration task file `netsecenv-task.yaml`. It could be modified by the user.

### Parents Selection
Parents are selected by a tournament selection, where `num_per_tournament` individuals compete and the one with the highest fitness score is selected. 
This competition is performed twice, once for each parent.
The selection of individuals to compete with each other can be done with or without replacement from pool of parents.
`num_per_tournament` is a hyperparameter that the user should set.

### Crossover Operator
Given two individuals (parents that were selected by tournament selection), they are combined using the "N-point crossover" approach, under some `prob_cross` probability.
N is a hyperparameter that the user should set, named `num_points`.
`prob_cross` is a hyperparameter that the user should set.

### Mutation Operator
Every action of every individual could be changed when a mutation operator is executed.
There are two possible mutation operators, each of which will be executed under some `mutation_prob` probability.
The different types of mutation operator are:
1. Mutation by action: the i-th action of the individual is changed by another possible action, chosen from the pool of all actions.
2. Mutation by parameter: in the i-th action of the individual only the parameters change, i.e. the action type does not change.
The choice between mutation operators is made under some `prob_parameter_mutation` probability.
`mutation_prob` and `prob_parameter_mutation` are hyperparameters that the user should set.

### Survivor Selection
After the crossover and mutation operators, an offspring is generated.
Parents and offspring are sorted by their fitness scores, and then a steady-state approach is performed: the worst `num_replace` individuals from the previous generation (parents) are replaced with the best `num_replace` individuals from the offspring.
`num_replace` is a hyperparameter that the user should set.

### Fitness Function
To evaluate each individual, the following is considered:
- A reward is given when a changing state is observed, no matter if the action is valid or not (e.g. FindServices on a host before performing the corresponding ScanNetwork is "invalid", but possible and the state will probably change, so it is rewarded). This is considered a "good action".
- If the state does not change but the action is "valid", it does not contribute to the reward (or it receives a slight penalty).
- Actions that do not change the state and are "invalid" are penalized. These are considered "bad actions".
- If an individual reaches the goal, it is rewarded with a big reward.
- The final reward is divided by a factor to minimize the number of steps.

### Termination Criteria
The algorithm stops when a maximum number of generations is reached, or when the fitness score reaches a maximum value.

