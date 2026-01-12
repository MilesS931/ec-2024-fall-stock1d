
# stock_population_evaluation.py

from cutting_stock.fitness_functions import *

# 1b TODO: Evaluate the population and assign the fitness
# member variable as described in the Assignment 1b notebook
def base_population_evaluation(population, **kwargs):
    # Use base_fitness_function, i.e.,
    # base_fitness_function(individual.genes, **kwargs)
    for individual in population:
        # Use base_fitness_function to calculate fitness
        output = base_fitness_function(individual.genes, **kwargs)
        # Assign the calculated fitness to the individual's fitness member variable
        individual.fitness = output['fitness']
    pass


# 1c TODO: Evaluate the population and assign the base_fitness, violations, and fitness
# member variables as described in the constraint satisfaction portion of Assignment 1c
def unconstrained_population_evaluation(population, penalty_coefficient, red=None, **kwargs):
    # Use unconstrained_fitness_function, i.e.,
    # unconstrained_fitness_function(individual.genes, **kwargs)
    if not red:
        # GREEN deliverable logic goes here
        for individual in population:
            # Use unconstrained_fitness_function to calculate fitness
            output = unconstrained_fitness_function(individual.genes, **kwargs)
            
            # Assign member variables based on the evaluation
            individual.base_fitness = output['base fitness']
            individual.violations = output['violations']
            individual.fitness = output['unconstrained fitness'] - individual.violations * penalty_coefficient
        
        pass

    else:
        # RED deliverable logic goes here
        pass


# 1d TODO: Evaluate the population and assign the objectives
# member variable as described in the multi-objective portion of Assignment 1d
def multiobjective_population_evaluation(population, yellow=None, **kwargs):
    # Use multiobjective_fitness_function, i.e.,
    # multiobjective_fitness_function(individual.genes, **kwargs)
    if not yellow:
        # GREEN deliverable logic goes here
        for individual in population:
            output = multiobjective_fitness_function(individual.genes, **kwargs)
            individual.objectives = [output['length'], output['width']]
            individual.length = output['length']
            individual.width = output['width']
        pass

    else:
        # YELLOW deliverable logic goes here
        pass

