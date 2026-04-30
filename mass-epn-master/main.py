import cProfile
import pstats

from functools import partial

from common.args import parser
from common.viewer import Viewer
from common.environment import Environment, virtual, boat, Node, Velocity
from common.units import deg, mps, DD
from osm import OSMSupplier

import path
import path.generators
from ga import Population

parser.parse_args()  # validate arguments

START_POINT = DD(54.21113807749146, 17.95494318008423)
END_POINT = DD(54.21409313095077, 17.95461058616638)
statics = OSMSupplier(START_POINT, 150).get_entities()

# 1. Polygon
statics.append(virtual([
    DD(54.21326498442491, 17.95486807823181),
    DD(54.21211057065281, 17.95370936393737),
    DD(54.21134512634103, 17.95598387718201)
]))


env = Environment(
    statics=statics,
    dynamics=[
        boat(DD(54.31271, 18.50224), 1 * mps, 40 * deg),
        boat(DD(54.31414, 18.50553), 0.5 * mps, 334 * deg)
    ]
)
bb = env.bounding_box

# path generator function yields nodes
path_generator = partial(path.generators.simplest_random,
                         start=Node(START_POINT, Velocity.HALF_AHEAD),
                         end=Node(END_POINT, Velocity.HALF_AHEAD),
                         nodes_range=(0, 10),
                         x_range=(bb[0], bb[2]),
                         y_range=(bb[1], bb[3]))


# path constructor is function used to generate single path
# path generator is used here to populate path with nodes
def path_constructor():
    return path.PathChromosome(
        nodes=[node for node in path_generator()],
        environment=env
    )


pop = Population(
    size=20,
    constructor=path_constructor,
)


# creating stats

with cProfile.Profile() as pr:
    history = [generation for generation in pop.run_generator(cost_target=1, max_generations=1000)]


stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.dump_stats('output.prof')


def weights_history(generations: list[Population]) -> dict[str, list[float]]:
    history = {}
    for gen in generations:
        for operation, weight in zip(gen.operations, gen.operation_weights):
            op = operation.__name__
            if op not in history:
                history[op] = []
            history[op].append(weight)
    return history


def costs_history(generations: list[Population]) -> dict[str, list[float]]:
    return {
        'maximal': [gen.max_cost for gen in generations],
        'average': [sum(gen.costs) / len(gen.costs) for gen in generations],
        'minimal': [gen.min_cost for gen in generations],
    }


# displaying stats and population history

operations_history = [gen.last_operation for gen in history]

Viewer(title="Operation weight history",
       draw=(weights_history(history), operations_history))
Viewer(title="Costs history",
       draw=(costs_history(history), operations_history))
Viewer(title="EPN", draw=[env, history[::10]])
