from common.types import Coords
from common.units import m

from . import DynamicEntity

AMOD25 = [2.15*m, 0.35*m]


def boat(position: Coords, velocity: float, course: float,
         size: tuple[float, float] = [1*m, 0.3*m]) -> DynamicEntity:

    def safe_zone(length, width):
        """Create a safe zone for a boat based on its length and width.\n
        Safe zone on prow is two lengths of ship, on stern it is half length
        of ship, sides have safe zone of one width, but the left one is doubled
        to force the genetic algorithm to avoid other ships on right side."""
        l = length  # noqa: E741
        hl = l / 2
        l2 = l * 2
        w = width
        hw = w / 2
        w2 = w * 2
        s = width  # side size
        return [
            # prow
            (-hw - w2, hl + l2 - s), (0, hl + l2), (hw + w, hl + l2 - s),
            # stern
            (hw + w, -hl - hl + s), (0, -hl - hl), (-hw - w2, -hl - hl + s),
        ]

    def model(length, width):
        """Create model of boat based on its length and width"""
        hl = length / 2
        hw = width / 2
        p = length / 5   # prow size
        s = length / 20  # stern size
        return [
            # prow
            (-hw, hl - p), (0, hl), (hw, hl - p),
            # stern
            (hw, -hl + s), (0, -hl), (-hw, -hl + s),
        ]

    entity = DynamicEntity(position, velocity, course, safe_zone(*size), model(*size))
    entity.category = 'boat'
    entity.model_color = 'white'
    return entity
