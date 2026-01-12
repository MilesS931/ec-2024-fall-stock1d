from math import inf
import math
import numpy as np


# TODO: Return True if A dominates B based on the objective member variables of both objects.
#       If attempting the YELLOW deliverable, your code must be able to gracefully handle
#       any number of objectives, i.e., don't hardcode an assumption that there are 2 objectives.
def dominates(A, B):
    # HINT: We strongly recommend use of the built-in functions any() and all()+
    return (all(a >= b for a, b in zip(A.objectives, B.objectives)) and
            any(a > b for a, b in zip(A.objectives, B.objectives)))
    pass


# TODO: Use the dominates function (above) to sort the input population into levels
#       of non-domination, and assign to the level members based on an individual's level.
def nondomination_sort(population):
    # Initialize structures
    domination_count = [0] * len(population)
    dominated_individuals = [set() for _ in range(len(population))]
    fronts = [[]]

    # Domination checks
    for i, A in enumerate(population):
        for j, B in enumerate(population):
            if i != j:
                if dominates(A, B):
                    dominated_individuals[i].add(j)
                elif dominates(B, A):
                    domination_count[i] += 1
        
        # Individuals with no dominators
        if domination_count[i] == 0:
            fronts[0].append(i)
            population[i].level = 1

    # Assign Levels
    current_front = 0
    while len(fronts) > current_front and fronts[current_front]:
        next_front = []
        for i in fronts[current_front]:
            for j in dominated_individuals[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    population[j].level = current_front + 2
                    next_front.append(j)
        current_front += 1
        fronts.append(next_front)

    # Cleanup empty last front if present
    if not fronts[-1]:
        fronts.pop()

    # Assign levels to each individual
    for level, front in enumerate(fronts, start=1):
        for idx in front:
            population[idx].level = level

    return fronts
        
    pass


# TODO: Calculate the crowding distance from https://ieeexplore.ieee.org/document/996017
#       For each individual in the population, and assign this value to the crowding member variable.
#       Use the inf constant (imported at the top of this file) to represent infinity where appropriate.
# IMPORTANT: Note that crowding should be calculated for each level of nondomination independently.
#            That is, only individuals within the same level should be compared against each other for crowding.
def assign_crowding_distances(population):
    # Don't forget to check for division by zero! Replace any divisions by zero with the inf constant.

    for level in set(individual.level for individual in population):
        # Collect all individuals in the current level
        current_level_individuals = [ind for ind in population if ind.level == level]
        
        # Initialize crowding distances
        for individual in current_level_individuals:
            individual.crowding = 0
        
        num_objectives = len(current_level_individuals[0].objectives)
        
        for i in range(num_objectives):
            # Sort the individuals based on the current objective
            current_level_individuals.sort(key=lambda ind: ind.objectives[i])
            
            # Set the boundary individuals' crowding distance to infinity
            current_level_individuals[0].crowding = inf
            current_level_individuals[-1].crowding = inf
            
            # Calculate crowding distances for all other individuals
            min_objective = current_level_individuals[0].objectives[i]
            max_objective = current_level_individuals[-1].objectives[i]
            
            if max_objective == min_objective:
                # Avoid division by zero
                continue
            
            for j in range(1, len(current_level_individuals) - 1):
                distance = (current_level_individuals[j + 1].objectives[i] - current_level_individuals[j - 1].objectives[i]) / (max_objective - min_objective)
                current_level_individuals[j].crowding += distance
    pass


# This function is implemented for you. You should not modify it.
# It uses the above functions to assign fitnesses to the population.
def assign_fitnesses(population, crowding, failure_fitness, **kwargs):
    # Assign levels of nondomination.
    nondomination_sort(population)

    # Assign fitnesses.
    max_level = max(map(lambda x:x.level, population))
    for individual in population:
        individual.fitness = max_level + 1 - individual.level

    # Check if we should apply crowding penalties.
    if not crowding:
        for individual in population:
            individual.crowding = 0

    # Apply crowding penalties.
    else:
        assign_crowding_distances(population)
        for individual in population:
            if individual.crowding != inf:
                assert 0 <= individual.crowding <= len(individual.objectives),\
                    f'A crowding distance ({individual.crowding}) was not in the correct range. ' +\
                    'Make sure you are calculating them correctly in assign_crowding_distances.'
                individual.fitness -= 1 - 0.999 * (individual.crowding / len(individual.objectives))




# The remainder of this file is code used to calculate hypervolumes.
# You do not need to read, modify or understand anything below this point.
# Implementation based on https://ieeexplore.ieee.org/document/5766730


def calculate_hypervolume(front, reference_point=None):
    point_set = [individual.objectives for individual in front]
    if reference_point is None:
        # Defaults to (-1)^n, which assumes the minimal possible scores are 0.
        reference_point = [-1] * len(point_set[0])
    return wfg_hypervolume(list(point_set), reference_point, True)


def wfg_hypervolume(pl, reference_point, preprocess=False):
    if preprocess:
        pl_set = {tuple(p) for p in pl}
        pl = list(pl_set)
        if len(pl[0]) >= 4:
            pl.sort(key=lambda x: x[0])

    if len(pl) == 0:
        return 0
    return sum([wfg_exclusive_hypervolume(pl, k, reference_point) for k in range(len(pl))])


def wfg_exclusive_hypervolume(pl, k, reference_point):
    return wfg_inclusive_hypervolume(pl[k], reference_point) - wfg_hypervolume(limit_set(pl, k), reference_point)


def wfg_inclusive_hypervolume(p, reference_point):
    return math.prod([abs(p[j] - reference_point[j]) for j in range(len(p))])


def limit_set(pl, k):
    ql = []
    for i in range(1, len(pl) - k):
        ql.append([min(pl[k][j], pl[k+i][j]) for j in range(len(pl[0]))])
    result = set()
    for i in range(len(ql)):
        interior = False
        for j in range(len(ql)):
            if i != j:
                if all(ql[j][d] >= ql[i][d] for d in range(len(ql[i]))) and any(ql[j][d] > ql[i][d] for d in range(len(ql[i]))):
                    interior = True
                    break
        if not interior:
            result.add(tuple(ql[i]))
    return list(result)
