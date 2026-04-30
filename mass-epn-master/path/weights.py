"""Weights used for Genetic Algorithm"""
from common.serialization import Serializable


class PathCost(Serializable):
    """Weights used to evaluate Path's cost"""
    DISTANCE = 1.0
    SMOOTHNESS = 60.0
    TIME = 1.0
    CLEARANCE = 1500.0
    CLEARANCE_STATIC = 1.0
    CLEARANCE_DYNAMIC = 1.0
