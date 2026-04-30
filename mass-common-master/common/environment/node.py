import numpy as np
from enum import Enum
from shapely.geometry import Point, LineString
from typing import Union
from common.ros.msg import ROSMsgInterface, NodeMsg, coords_to_ros_msg, coords_from_ros_msg

from common.serialization import Serializable
from common.types import Coords
from common.units import deg, toCD, toDD


class Velocity(float, Enum):
    """Defined velocities of boat"""
    SLOW_AHEAD = 1.0
    HALF_AHEAD = 2.0
    FULL_AHEAD = 4.0


class Node(Serializable, ROSMsgInterface):
    """A path's node"""
    position: Coords
    point: Point
    velocity: Velocity
    course: float = None  # TODO: change course to be in radians
    index: int = None

    def __init__(self, position: Coords, velocity: Velocity):
        self.position = position
        self.point = Point(position)
        self.velocity = velocity

    def copy(self) -> 'Node':
        cls = self.__class__
        new = cls(self.position, self.velocity)
        new.course = self.course
        new.index = self.index
        return new

    def set_course(self, next: 'Node'):
        """Calculates and sets course of Node

        Args:
            next (Node): Node to where set course
        """
        x1, y1 = self.position
        x2, y2 = next.position
        dx, dy = x2 - x1, y2 - y1

        course = 90 - np.arctan2(dy, dx) / deg
        if course <= 0:
            course = 360 + course

        self.course = course

    def course_change(self, previous: 'Node') -> float:
        """Calculates the turn angle from a given node to the current node

        Args:
            previous: Node from which the turn is taken

        Returns:
            Turn angle (in degrees)
        """
        angle = abs(self.course - previous.course)
        if angle > 180:
            angle = abs(angle - 360)
        return angle

    def time_of_arrival(self, destination: Union[Coords, 'Node']) -> float:
        """Calculates time of arrival to given destination

        Args:
            destination: Node/Coords, toward which TOA is calculated

        Returns:
            Time of arrival to given destination (in seconds):
        """
        if isinstance(destination, Node):
            destination = destination.position
        line = LineString([self.position, destination])
        return line.length / self.velocity

    def serialize(self) -> dict:
        return {
            "position": self.position,
            "velocity": float(self.velocity),
            "course": self.course,
        }

    def deserialize(self, dictionary: dict):
        super().deserialize(dictionary)
        self.position = tuple(dictionary['position'])
        self.point = Point(self.position)
        self.velocity = Velocity(dictionary['velocity'])

    def __repr__(self) -> str:
        return (
            'Node('
            f'pos=[{self.position[0]:.2f};{self.position[1]:.2f}], '
            f'velocity={self.velocity.name})'
        )

    def __str__(self) -> str:
        lat, lon = toDD(*self.position)
        course = self.course or 0
        i = self.index
        if i == 0:
            i = 'Start'
        elif i == -1:
            i = 'End'
        else:
            i = f'Node{i}'
        return (
            f'<b>{i} {lat:.4f}; {lon:.4f}</b><br>'
            f'Velocity: {self.velocity.name}<br>'
            f'Course: {course:.0f}° ({toCD(course)})'
        )

    def to_ros_msg(self) -> NodeMsg:
        return NodeMsg(
            position=coords_to_ros_msg(self.position),
            velocity=self.velocity,
            course=self.course
        )

    @classmethod
    def from_ros_msg(cls, ros_msg: NodeMsg) -> 'Node':
        c = cls(coords_from_ros_msg(ros_msg.position), ros_msg.velocity)
        c.course = ros_msg.course
        c.index = ros_msg.index
        return c
