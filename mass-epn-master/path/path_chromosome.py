from functools import cache

from shapely.geometry import LineString

from common.environment import Environment, Path, Node

from ga.chromosome import Chromosome

from .weights import PathCost

CACHE_ALL_COSTS = True

conditional_cache = cache if CACHE_ALL_COSTS else lambda x: x


class PathChromosome(Path, Chromosome):
    environment: Environment

    def __init__(self, nodes: list[Node], environment: Environment):
        super().__init__(nodes)
        self.environment = environment

    def copy(self):
        cls = self.__class__
        new = cls([node.copy() for node in self.nodes], self.environment)
        new.feasible = self.feasible
        new.generation = self.generation
        new.created_generation = self.created_generation
        new.created_with = self.created_with
        return new

    @conditional_cache
    def distance_cost(self) -> float:
        """Cost is a length of path."""
        return self.line.length

    @conditional_cache
    def smooth_cost(self) -> float:
        """Cost is a sum of course changes."""

        # do not calculate angle for end node
        return sum([(node.course_change(prev_node) ** 2)
                    for prev_node, node in zip(self.nodes[:-2], self.nodes[1:-1])])

    @conditional_cache
    def clearance_static_cost(self) -> float:
        """Cost is a length of path which intersects static objects.

        Judges feasibility of path, sets `feasible` attribute.
        """
        intersection = 0.0
        for ent in self.environment.statics:
            # if not only touches exterior but also intersects with interior
            if not self.line.touches(ent.safe_zone) and self.line.intersects(ent.safe_zone):
                intersection += self.line.intersection(ent.safe_zone).length ** 2

        self.feasible = intersection == 0.0
        return intersection

    @conditional_cache
    def clearance_dynamic_cost(self) -> float:
        """Cost is a length of path which intersects dynamic objects.

        Dynamic cost is not calculated for unfeasible paths.
        """
        if self.feasible is None or not self.feasible:
            return 0.0

        intersection_length = 0.0
        for ent in self.environment.dynamics:
            # calculate potential collision points (actually lines)
            pot_collisions = []
            time = 0
            for node, next_node in zip(self.nodes[:-1], self.nodes[1:]):
                line = LineString([node.position, next_node.position])
                if line.intersects(ent.trajectory):
                    intersection = line.intersection(ent.trajectory)
                    time_range = []
                    for coords in intersection.coords:
                        time_range.append(time + node.time_of_arrival(coords))
                    pot_collisions.append(tuple([intersection, time_range]))
                time += node.time_of_arrival(next_node)

            # check if potential collisions are actually a collision
            for col_point in pot_collisions:
                intersection, times = col_point
                for index in range(0, 2):
                    _, safe_zone, _ = ent.calculate_position(times[index])
                    if safe_zone.contains(intersection.boundary.geoms[index]):
                        intersection_length += intersection.length / 2

        return intersection_length

    @conditional_cache
    def clearance_cost(self) -> float:
        """Cost is a weighted sum of static and dynamic cost."""
        static = self.clearance_static_cost()
        dynamic = self.clearance_dynamic_cost()
        return (
            static * PathCost.CLEARANCE_STATIC +
            dynamic * PathCost.CLEARANCE_DYNAMIC
        )

    @conditional_cache
    def time_cost(self) -> float:
        """Cost is a total time of arrival to destination."""
        return sum([node.time_of_arrival(next_node)
                    for node, next_node in zip(self.nodes[:-1], self.nodes[1:])])

    @cache
    def cost(self) -> float:
        """Weighted cost of path."""
        return (
            self.distance_cost() * PathCost.DISTANCE +
            self.smooth_cost() * PathCost.SMOOTHNESS +
            self.clearance_cost() * PathCost.CLEARANCE +
            self.time_cost() * PathCost.TIME
        )

    def __str__(self) -> str:
        if self.created_generation != 0:
            creation = (f'Created in gen <b>{self.created_generation}</b><br>'
                        f'with <b>{self.created_with}</b>'
                        )
        else:
            creation = 'Created on <b>start</b><br>with path generator'
        return super().__str__(f' (gen {self.generation})') + (
            f'<br><i>{creation}</i><br>'
            f'<b>Costs:</b> {self.cost():.2E}<br>'
            f'Distance: {self.distance_cost():.2E}<br>'
            f'Smooth: {self.smooth_cost():.2E}<br>'
            f'Clearance:{self.clearance_cost():.2E}<br>'
            f' - static: {self.clearance_static_cost():.2E}<br>'
            f' - dynamic: {self.clearance_dynamic_cost():.2E}<br>'
            f'Time: {self.time_cost():.2f}<br>'
        )
