from typing import Callable, Union

from .args import parser
from .chromosome import Chromosome

GeneticOperation = Callable[[list[Chromosome]], Chromosome]


class OperationError(Exception):
    pass


_operations = []
_weights = []
_chromosomes_count = dict()

args, _ = parser.parse_known_args()
SKIP_TAGS = {'skip', 'unimplemented', *args.operations_skip}


def genetic_operation(*args, weight: float = 1.0, chromosomes: int = 1,
                      tags: Union[str, list[str]] = None):
    if tags is None:
        tags = []
    elif isinstance(tags, str):
        tags = [tags]

    def decorator(func):
        for name in {func.__name__, *func.__name__.split('_')}:
            tags.append(name)
        if len(set(tags).intersection(SKIP_TAGS)) == 0:  # no `tags` in `SKIP_TAGS`
            _operations.append(func)
            _weights.append(weight)
            _chromosomes_count[func] = chromosomes
        return func

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])
    else:
        return decorator


def get_list() -> list[GeneticOperation]:
    return _operations.copy()


def get_chromosomes_count(func) -> int:
    return _chromosomes_count[func]


def get_weights() -> list[float]:
    return _weights.copy()
