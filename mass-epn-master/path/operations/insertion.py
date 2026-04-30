import random

from common.environment import Node
from ga import genetic_operation

from ..path_chromosome import PathChromosome


@genetic_operation
def insertion(parents: list[PathChromosome]) -> PathChromosome:
    """Insert randomly generated (in scope of bounding box) waypoint in random place"""
    parent = parents[0]

    node_index = 1 if len(parent.nodes) == 2 else random.randrange(1, len(parent.nodes) - 1)

    xmin, ymin, xmax, ymax = parent.environment.bounding_box
    child = parent.copy()
    node = Node((random.uniform(xmin, xmax), random.uniform(ymin, ymax)),
                parent.nodes[node_index].velocity)
    child.nodes.insert(node_index, node)
    child.update()

    return child
