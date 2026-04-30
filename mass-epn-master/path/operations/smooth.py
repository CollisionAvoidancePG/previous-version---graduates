from ga import genetic_operation, OperationError

from ..path_chromosome import PathChromosome


@genetic_operation
def smooth(parents: list[PathChromosome]) -> PathChromosome:
    """Remove waypoint causing max course change"""
    parent = parents[0]
    if len(parent.nodes) <= 2:
        raise OperationError("Path has too few nodes for this operation")
    course_changes = [node.course_change(prev_node)
                      for prev_node, node in zip(parent.nodes[:-2], parent.nodes[1:-1])]
    max_index = course_changes.index(max(course_changes)) + 1

    child = parent.copy()
    child.nodes.pop(max_index)
    child.update()
    return child
