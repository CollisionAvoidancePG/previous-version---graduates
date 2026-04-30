import random

from ga import genetic_operation, OperationError

from ..path_chromosome import PathChromosome


@genetic_operation
def deletion(parents: list[PathChromosome]) -> PathChromosome:
    """Delete random waypoint from path"""
    parent = parents[0]
    if len(parent.nodes) <= 2:
        raise OperationError("Path has only start and end node")

    child = parent.copy()
    child.nodes.pop(random.randrange(1, len(child.nodes) - 1))
    child.update()
    return child
