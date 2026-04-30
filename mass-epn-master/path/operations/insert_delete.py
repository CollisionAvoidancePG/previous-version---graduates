from ga import genetic_operation

from ..path_chromosome import PathChromosome


@genetic_operation(tags='unimplemented')
def insert_delete(parents: list[PathChromosome]) -> PathChromosome:
    """TBD"""
    parent = parents[0]
    child = parent.copy()
    return child
