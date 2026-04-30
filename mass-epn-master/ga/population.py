from random import choices
from typing import Callable

from common.serialization import Serializable
from common import logging

from . import operation as op
from .chromosome import Chromosome
from .operation import GeneticOperation, OperationError
from .args import parser

MIN_WEIGHT = 0.01

log = logging.getLogger(__name__)

args, _ = parser.parse_known_args()

ChromosomeConstructor = Callable[[], Chromosome]

log.info(f'Operations evaluation {"enabled" if args.operations_evaluation else "DISABLED"}')


class Population(Serializable):
    """Population of chromosomes"""
    total_generations: int  # count total generations since creation
    chromosomes: list[Chromosome]
    costs: list[float]
    min_cost: float
    max_cost: float
    operations: list[GeneticOperation]
    operation_weights: list[float]
    last_operation: str = None

    def __init__(self, *, size: int, constructor: ChromosomeConstructor):
        self.total_generations = 0
        self.operations = op.get_list()
        self.operation_weights = op.get_weights()
        self.chromosomes = [constructor() for _ in range(size)]
        self.update()

    def copy(self) -> 'Population':
        """Copy current population state"""
        cls = self.__class__
        new = object.__new__(cls)
        new.total_generations = self.total_generations
        new.chromosomes = [c.copy() for c in self.chromosomes]
        new.costs = self.costs.copy()
        new.min_cost = self.min_cost
        new.max_cost = self.max_cost
        new.operations = self.operations.copy()
        new.operation_weights = self.operation_weights.copy()
        new.last_operation = self.last_operation
        return new

    def run(self, *, cost_target: float, max_generations: int):
        [_ for _ in self.run_generator(
            cost_target=cost_target,
            max_generations=max_generations,
            yield_history=False
        )]

    def run_generator(self, *, cost_target: float, max_generations: int,
                      yield_history: bool = True) -> 'Population':
        """Run population evolution for desired targets

        Args:
            cost_target (float): Cost target
            max_generations (int): Max number of generation in this run
            history (bool): Should snapshots (copies) of population be yielded on each iteration

        Yields:
            Iterator[Population]: Snapshot (copy) of each generation if history is enabled
        """
        log.info(f'Running population ({cost_target=}, {max_generations=})')
        try:
            for i in range(max_generations):
                log.debug(
                    f'Generation: {i} / {max_generations}, '
                    f'Cost: min={self.min_cost:.2f} > target={cost_target:.2f}'
                )
                if self.min_cost <= cost_target:
                    break
                yield self.copy() if yield_history else None  # yield generation
                self.total_generations += 1
                self.evolve()
                for ch in self.chromosomes:
                    ch.generation = self.total_generations

            yield self.copy() if yield_history else None  # yield last generation
        except OperationError as e:
            log.error(e)
        log.info('Population run done')

    def update(self):
        """Sort and calculate costs"""
        self.chromosomes.sort(key=lambda x: x.cost())
        self.costs = [c.cost() for c in self.chromosomes]
        self.min_cost = self.costs[0]
        self.max_cost = self.costs[-1]

    def pick(self, count: int) -> list[Chromosome]:
        """Picks number of chromosomes for genetic operations with weights (fitness)
        based on Paths' cost. The bigger the cost of chromosome is the lower chance
        it has to be picked."""
        fitness = [1 / cost * self.max_cost for cost in self.costs]
        return choices(
            population=self.chromosomes,
            weights=fitness,
            k=count
        )

    def evolve(self):
        """Perform a genetic operation on population."""
        operations = self.operations.copy()
        weights = self.operation_weights.copy()
        while True:
            # the following statement is not true, but it is unlikely to happen
            if len(operations) == 0:
                raise OperationError("This population cannot evolve further")

            operation: GeneticOperation = choices(
                population=operations,
                weights=weights,
                k=1
            )[0]

            selected = self.pick(op.get_chromosomes_count(operation))

            # TODO: iterate over all chromosomes before removing operation from
            # TODO: operations list, this should cover all cases
            # check if operation is possible, if not go with another one
            try:
                new = operation(selected)
            except OperationError:
                index = operations.index(operation)
                operations.pop(index)
                weights.pop(index)
                continue

            new.created_generation = self.total_generations
            new.created_with = operation.__name__
            self.last_operation = operation.__name__
            self.replace(new)
            self.evaluate_operation(operation, new, selected[0])
            return

    def replace(self, chromosome: Chromosome):
        """Remove chromosomes that has biggest cost and add new one"""
        self.chromosomes.pop()
        self.chromosomes.append(chromosome)
        self.update()

    def evaluate_operation(self, operation: GeneticOperation, new: Chromosome, old: Chromosome):
        """Evaluate efficiency of genetic operation and add weight"""
        if not args.operations_evaluation:
            return
        new_cost = new.cost()
        old_cost = old.cost()
        weight = old_cost - new_cost
        index = self.operations.index(operation)
        self.operation_weights[index] = max(self.operation_weights[index] + weight, MIN_WEIGHT)

    def draw(self, go, fig):
        for chromosome in self.chromosomes:
            chromosome.draw(go, fig)

    def __repr__(self) -> str:
        avg = sum(self.costs) / len(self.costs)
        return (
            'Population('
            f'size={len(self.chromosomes)}, '
            f'generations={self.total_generations}'
            f'cost=[{avg:.2f};{self.min_cost:.2f};{self.max_cost:.2f}])'
        )

    def __str__(self) -> str:
        avg = sum(self.costs) / len(self.costs)
        ops = zip(self.operations, self.operation_weights)
        ops = "<br>  - ".join("{0} = {1:.2f}".format(x[0].__name__, y) for x, y in ops)
        return (
            '<b>Population summary:</b><br>'
            f'- size = {len(self.chromosomes)}<br>'
            f'- generations = {self.total_generations}<br>'
            '<b>- chromosome costs:</b><br>'
            f'  - avg = {avg:.2f}<br>'
            f'  - min = {self.min_cost:.2f}<br>'
            f'  - max = {self.max_cost:.2f}<br>'
            '<b>- operation weights:</b> '
            f'<i>(evaluation {"disabled" if args.evaluation_disable else "enabled"})</i><br>'
            f'  - {ops}'
        )
