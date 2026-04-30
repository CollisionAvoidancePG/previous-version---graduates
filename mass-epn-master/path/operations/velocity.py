import random

from common.environment import Velocity
from ga import genetic_operation, OperationError

from ..path_chromosome import PathChromosome


@genetic_operation(tags='skip')
def mutation_velocity(parents: list[PathChromosome]) -> PathChromosome:
    """Change velocity of random waypoint"""
    parent = parents[0]
    if len(parent.nodes) <= 2:
        raise OperationError("Path has only start and end node")

    velocities = list(Velocity)
    mutations = [-1, 0, 1]  # possible mutations

    child = parent.copy()
    node_id = random.randrange(1, len(parent.nodes) - 1)
    velocity_id = velocities.index(child.nodes[node_id].velocity)

    # remove mutations for border velocities
    if velocity_id == 0:
        mutations.pop(0)
    elif velocity_id == len(velocities) - 1:
        mutations.pop(-1)

    mutation = random.choice(mutations)  # selected mutation
    velocity = velocities[velocity_id + mutation]  # apply mutation

    child.nodes[node_id].velocity = velocity
    child.update()
    return child
