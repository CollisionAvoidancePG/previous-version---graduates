import random

from ga import genetic_operation, OperationError

from ..path_chromosome import PathChromosome


@genetic_operation
def swap(parents: list[PathChromosome]) -> PathChromosome:
    """Swap order of two random waypoints in path"""
    parent = parents[0]
    if len(parent.nodes) <= 3:
        raise OperationError("Path has too few nodes for this operation")
    node_index1 = random.randrange(1, len(parent.nodes) - 2)
    node_index2 = node_index1 + 1

    child = parent.copy()
    child.nodes.pop(node_index1)
    child.nodes.insert(node_index1, parent.nodes[node_index2])
    child.nodes.pop(node_index2)
    child.nodes.insert(node_index2, parent.nodes[node_index1])
    child.update()

    return child
