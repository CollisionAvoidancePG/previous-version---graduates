import random
from typing import Union

from .types import Range


def uni_randrange_single(i: Union[int, float, Range]) -> int:
    """Universal `randrange`, it accepts `int` or `Range`"""
    if isinstance(i, tuple):
        return random.uniform(*i)
    elif isinstance(i, int):
        return random.randrange(i)
    elif isinstance(i, float):
        return random.uniform(0, i)


def uni_randrange(*args: Union[int, float, Range]) -> Union[int, float, tuple]:
    """Universal `randrange`, it accepts multiple `int` or `Range`"""
    result = [uni_randrange_single(i) for i in args]
    return result[0] if len(result) == 1 else result
