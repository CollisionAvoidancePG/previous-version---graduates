import random

from common.environment import Node
from ga import genetic_operation, OperationError

from ..path_chromosome import PathChromosome


@genetic_operation(weight=4.0)
def mutation_fine(parents: list[PathChromosome]) -> PathChromosome:
    """
    Replace random waypoint in path with randomly generated (in scope of bounding box), safe point
    """
    parent = parents[0]
    if len(parent.nodes) <= 2:
        raise OperationError("Path has only start and end node")

    node_index = random.randrange(1, len(parent.nodes) - 1)
    xmin, ymin, xmax, ymax = parent.environment.bounding_box
    child = parent.copy()
    child.nodes.pop(node_index)
    while True:
        intersects = False
        node = Node((random.uniform(xmin, xmax), random.uniform(ymin, ymax)),
                    parent.nodes[node_index].velocity)
        for static in parent.environment.statics:
            if node.point.intersects(static.safe_zone):
                intersects = True
                break
        if not intersects:
            break
    child.nodes.insert(node_index, node)
    child.update()

    return child


@genetic_operation(weight=4.0)
def mutation_random(parents: list[PathChromosome]) -> PathChromosome:
    """Replace random waypoint in path with randomly generated (in scope of bounding box), point"""
    parent = parents[0]
    if len(parent.nodes) <= 2:
        raise OperationError("Path has only start and end node")

    node_index = random.randrange(1, len(parent.nodes) - 1)
    xmin, ymin, xmax, ymax = parent.environment.bounding_box
    child = parent.copy()
    child.nodes.pop(node_index)
    node = Node((random.uniform(xmin, xmax), random.uniform(ymin, ymax)),
                parent.nodes[node_index].velocity)
    child.nodes.insert(node_index, node)
    child.update()

    return child
