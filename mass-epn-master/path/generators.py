import random
from common.types import Range
from common.random import uni_randrange

from common.environment import Node, Velocity


def simplest_random(*, start: Node, end: Node, nodes_range: Range,
                    x_range: Range, y_range: Range) -> Node:
    velocities = list(Velocity)
    yield start
    for _ in range(int(uni_randrange(nodes_range))):
        position = uni_randrange(x_range, y_range)
        yield Node(position, random.choice(velocities))
    yield end
