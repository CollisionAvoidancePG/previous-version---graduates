import random

from ga import genetic_operation, OperationError

from ..path_chromosome import PathChromosome


@genetic_operation(chromosomes=2)
def crossover(parents: list[PathChromosome]) -> PathChromosome:
    """Slice parents in random point and create offspring by merging these two parts"""
    parent1, parent2, *_ = parents

    # if any of parents would have only 3 nodes, child would be same as one of the parents
    if len(parent1.nodes) <= 3 or len(parent2.nodes) <= 3:
        raise OperationError("Path has too few nodes for this operation")

    child = parent1.copy()
    crossover_point = random.randrange(2, min(len(parent1.nodes) - 1, len(parent2.nodes) - 1))

    del child.nodes[crossover_point:len(parent1.nodes)]
    child.nodes.extend(parent2.nodes[crossover_point:len(parent2.nodes)])
    child.update()
    return child
