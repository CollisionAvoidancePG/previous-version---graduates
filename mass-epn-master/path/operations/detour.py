import numpy as np

from shapely.geometry import LineString
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from common.environment import Environment, Node, StaticEntity, Velocity
from common.types import CoordsList
from ga import genetic_operation, OperationError

from ..path_chromosome import PathChromosome


@genetic_operation(weight=10.0)
def detour(parents: list[PathChromosome]) -> PathChromosome:
    """Finds the first obstacle in the path and goes around it to the first safe waypoint.
    Operation uses dijkstra algorithm to find the shortest path"""
    parent = parents[0]
    child = parent.copy()

    node_index, next_node_index, obstacle = find_first_obstacle(parent)

    # remove all following nodes inside obstacle
    for node in child.nodes[next_node_index:]:
        if obstacle.safe_zone.contains(node.point):
            child.nodes.remove(node)
        else:
            break

    coords, graph = create_graph(child.nodes[node_index], child.nodes[next_node_index], obstacle,
                                 child.environment)

    # calculate the shortest path using dijkstra algorithm
    _, predecessors = dijkstra(csgraph=graph, directed=False, indices=-1, return_predecessors=True)

    new_nodes = retrieve_nodes(predecessors, coords)

    for new_node in new_nodes:
        child.nodes.insert(next_node_index, new_node)
        next_node_index = next_node_index + 1

    child.update()
    return child


"""
Helper functions
"""


def find_first_obstacle(path: PathChromosome) -> tuple[int, int, StaticEntity]:
    """Find first obstacle in path

    Returns:
        indexes of nodes between which there is an obstacle
        first obstacle on the path
    """
    for node, next_node in zip(path.nodes[:-1], path.nodes[1:]):
        segment = LineString([node.position, next_node.position])
        for ent in path.environment.statics:
            if segment.intersects(ent.safe_zone):
                return path.nodes.index(node), path.nodes.index(next_node), ent

    raise OperationError("Path does not intersect any static obstacles")


def create_obstacle_graph(obstacle: StaticEntity, env: Environment):
    """Generate graph for obstacle nodes and keep it as StaticEntity member"""
    coords = [obstacle_coord for obstacle_coord in obstacle.safe_zone.exterior.coords]

    # also allocate memory for start and end nodes
    graph = [[None for _ in range(len(coords) + 2)] for _ in range(len(coords) + 2)]

    for i in range(len(coords)):
        for j in range(len(coords)):
            if graph[i][j] is not None:
                continue
            elif i == j:
                graph[i][j] = 0
                continue

            nodes = [Node(coords[i], Velocity.FULL_AHEAD), Node(coords[j], Velocity.FULL_AHEAD)]
            path_segment = PathChromosome(nodes, env)

            if path_segment.clearance_static_cost() != 0:
                segment_cost = np.Inf
            else:
                segment_cost = path_segment.line.length

            # Graph is symmetrical. Path from point A to point B has the same cost as path from
            # point B to A
            graph[i][j] = graph[j][i] = segment_cost

    obstacle.graph = graph


def create_graph(start_node: Node, end_node: Node, obstacle: StaticEntity,
                 env: Environment) -> tuple[CoordsList, csr_matrix]:
    """Complement obstacle graph by including start and end nodes

    Args:
        start_node:
        end_node:
        obstacle: Obstacle to detour
        env:

    Returns:
        coords: Coordinates of obstacle vertices and start, end nodes
        graph: Paths costs for each coords pair
    """
    if obstacle.graph is None:
        create_obstacle_graph(obstacle, env)

    graph = obstacle.graph
    coords = [obstacle_coord for obstacle_coord in obstacle.safe_zone.exterior.coords]
    coords.extend([start_node.position, end_node.position])

    for i in range(len(coords)):
        for j in range(-2, 0):
            if graph[i][j] is not None:
                continue
            elif i == j:
                graph[i][j] = 0
                continue

            nodes = [Node(coords[i], Velocity.FULL_AHEAD), Node(coords[j], Velocity.FULL_AHEAD)]
            path_segment = PathChromosome(nodes, env)

            if path_segment.clearance_static_cost() != 0:
                segment_cost = np.Inf
            else:
                segment_cost = path_segment.line.length

            # Graph is symmetrical. Path from point A to point B has the same cost as path from
            # point B to A
            graph[i][j] = graph[j][i] = segment_cost

    return coords, csr_matrix(graph)


def retrieve_nodes(predecessors: np.shape, coords: CoordsList) -> list[Node]:
    """Retrieve nodes from predecessors

    Args:
        predecessors: The matrix of predecessors, which can be used to reconstruct
        the shortest path

    Returns: Nodes in sequence

    """
    nodes = []
    current_index = predecessors[-2]

    while predecessors[current_index] != -9999:
        nodes.append(Node(coords[current_index], Velocity.FULL_AHEAD))
        current_index = predecessors[current_index]

    return nodes
