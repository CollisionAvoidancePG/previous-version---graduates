# autopep8: off
from pathlib import Path
import sys

import pytest
sys.path.insert(1, str(Path(__file__).parent.parent))
sys.argv = ['']

import random

from common.environment import Environment, Node, Velocity, StaticEntity
from common.viewer import Viewer
from path import PathChromosome
from path.operations.crossover import crossover
from path.operations.deletion import deletion
from path.operations.insertion import insertion
from path.operations.detour import detour
from path.operations.smooth import smooth
from path.operations.swap import swap
from path.operations.mutation import *  # noqa: F403
from path.operations.velocity import mutation_velocity

statics = [StaticEntity([(0, 2), (1, 1.5), (1.5, 1), (2, 0), (1.5, -1), (0, -2), (-1, -1.5),
                        (0, 0), (-2, 0), (-1, 1.5)], safe_zone_size=.05)]


min = 3.2
max = 3.3
statics.append(StaticEntity([(min, min), (max, min), (max, max), (min, max)], safe_zone_size=0))
statics.append(StaticEntity([(-min, min), (-max, min), (-max, max), (-min, max)], safe_zone_size=0))
statics.append(StaticEntity([(min, -min), (max, -min), (max, -max), (min, -max)], safe_zone_size=0))
statics.append(StaticEntity([(-min, -min), (-max, -min), (-max, -max), (-min, -max)],
                            safe_zone_size=0))

env = Environment(
    statics=statics,
    dynamics=[]
)

PATH1 = [(-2, -2), (-1, 1), (1, 0), (1, 2), (3, 0)]
PATH2 = [(-2, -2), (-2, 1), (-1, 2), (0, 1), (3, 0)]


@pytest.fixture
def parents():
    return [
        PathChromosome([Node(p, Velocity.FULL_AHEAD) for p in PATH1], environment=env),
        PathChromosome([Node(p, Velocity.FULL_AHEAD) for p in PATH2], environment=env)
    ]


@pytest.fixture
def parent(parents):
    return [parents[0]]


def test_crossover(parents):
    child = crossover(parents)
    Viewer(title="Operator: crossover", draw=[env, child, *parents])


def test_deletion(parent):
    child = deletion(parent)
    Viewer(title="Operator: deletion", draw=[env, child, *parent])
    assert len(child.nodes) < len(parent[0].nodes)


def test_detour(parent):
    child = detour(parent)
    Viewer(title="Operator: detour", draw=[env, child, *parent])


def test_insertion(parent):
    child = insertion(parent)
    Viewer(title="Operator: insertion", draw=[env, child, *parent])
    assert (len(child.nodes) - len(parent[0].nodes)) == 1


def test_smooth(parent):
    child = smooth(parent)
    Viewer(title="Operator: smooth", draw=[env, child, *parent])


def test_swap(parent):
    child = swap(parent)
    Viewer(title="Operator: swap", draw=[env, child, *parent])


def test_mutation_fine(parent):
    child = mutation_fine(parent)  # noqa: F405
    Viewer(title="Operator: mutation fine", draw=[env, child, *parent])


def test_mutation_random(parent):
    child = mutation_random(parent)  # noqa: F405
    Viewer(title="Operator: mutation random", draw=[env, child, *parent])


def test_mutation_velocity():
    velocities = list(Velocity)
    parents = [
        PathChromosome([Node(p, random.choices(velocities)[0]) for p in PATH1], environment=env),
    ]
    child = mutation_velocity(parents)
    Viewer(title="Operator: mutation speed", draw=[env, child, *parents])
