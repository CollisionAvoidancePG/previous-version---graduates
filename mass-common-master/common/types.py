from collections import namedtuple
from typing import Union

# this can be later changed to 'namedtuple' with x and y
Coords = namedtuple('Coords', ['x', 'y'])
CoordsList = list[Coords]

BoundingBox = namedtuple('BoundingBox', ['xmin', 'ymin', 'xmax', 'ymax'])

RangeMax = int
RangeMinMax = tuple[int, int]
Range = Union[RangeMax, RangeMinMax]
