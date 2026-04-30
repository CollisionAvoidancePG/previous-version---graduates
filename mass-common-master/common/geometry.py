import numpy as np

from common.types import Coords


def vector(distance: float = 1.0, angle: float = 0.0) -> Coords:
    """Calculate vector of distance in given angle"""
    return distance * np.sin(angle), distance * np.cos(angle)
