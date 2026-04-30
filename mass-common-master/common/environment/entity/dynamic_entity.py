from shapely.geometry import Point, Polygon
from shapely.affinity import translate, rotate
from common.geometry import vector
from common.ros.msg import (ROSMsgInterface, DynamicEntityMsg, DynamicEntitiesMsg,
                            coords_from_ros_msg, coords_to_ros_msg)
from common.types import Coords, CoordsList
from common.units import deg, toCD
from . import Entity

from .args import parser

args, _ = parser.parse_known_args()

MAX = 1000


class DynamicEntity(Entity, ROSMsgInterface):
    """Dynamic environment entity that has collision and can move.

    For example: boats, ships
    """
    position: Coords
    point: Point
    velocity: float
    course: float
    trajectory: Polygon
    hover_info: bool = True
    __resolved: bool = False

    def __init__(self, position: Coords, velocity: float, course: float,
                 safe_zone: CoordsList, model: CoordsList):
        super().__init__(safe_zone, model)
        i = len(safe_zone) // 2
        self.position = position
        self.point = Point(position)
        self.velocity = velocity
        self.course = course
        self.calculate_trajectory(safe_zone[:i], safe_zone[i:])

    def copy(self) -> "DynamicEntity":
        d = DynamicEntity(self.position, self.velocity, self.course, self.safe_zone.exterior.coords,
                          self.model.exterior.coords)
        d.category = self.category
        return d

    def resolve(self):
        """Irreversibly transform safe zone and model polygons"""
        if self.__resolved:
            return
        self.point, self.safe_zone, self.model = self.calculate_position()
        self.__resolved = True

    def calculate_position(self, time: float = 0) -> tuple[Point, Polygon, Polygon]:
        """Calculate object position after the given time"""
        if self.__resolved:
            raise RuntimeError("DynamicEntity has been already resolved")
        delta = vector(self.velocity * time, self.course)
        point = translate(self.point, *delta)

        delta = (point.x, point.y)
        safe_zone = translate(self.safe_zone, *delta)
        safe_zone = rotate(safe_zone, -self.course, origin=point, use_radians=True)

        model = self.model
        if model is not None:
            model = translate(model, *delta)
            model = rotate(model, -self.course, origin=point, use_radians=True)

        return point, safe_zone, model

    def calculate_trajectory(self, front, back):
        """Calculate DynamicObject safe zone trajectory and store it.\n
        First half of its safe zone should be the front, otherwise it won't be
        calculated correctly."""
        front = [(x, y + MAX) for x, y in front]
        trajectory = Polygon(front + back)

        position, safe_zone, model = self.calculate_position()
        trajectory = translate(trajectory, *self.position)
        self.trajectory = rotate(trajectory, -self.course, origin=position, use_radians=True)

    def draw(self, go, fig):
        _, safe_zone, model = self.calculate_position()

        self._draw_polygon(go, fig, self.trajectory, 'black', opacity=0.1)

        # Draw DynamicObject at calculated position
        self._draw_polygon(go, fig, safe_zone, self.safe_zone_color, opacity=0.2)
        if not args.models_disabled:
            self._draw_polygon(go, fig, model, self.model_color)

    def serialize(self) -> dict:
        return super().serialize() | {
            "position": self.position,
            "velocity": self.velocity,
            "course": self.course,
        }

    def deserialize(self, dictionary: dict):
        super().deserialize(dictionary)
        self.position = tuple(dictionary['position'])
        self.point = Point(self.position)

    def __repr__(self) -> str:
        return ('DynamicEntity('
                f'pos=[{self.position[0]:.2f};{self.position[1]:.2f}], '
                f'velocity={self.velocity:.2f} m/s'
                f'course={(self.course / deg):.0f}°) ({toCD(self.course / deg)})')

    def __str__(self) -> str:
        return (
            f'<b>{self.__class__.__name__}:{self.category}</b><br>'
            f'Velocity: {self.velocity:.1f} m/s<br>'
            f'Course: {self.course / deg:.0f}° ({toCD(self.course / deg)})'
        )

    def to_ros_msg(self) -> DynamicEntityMsg:
        return DynamicEntityMsg(
            category=self.category,
            position=coords_to_ros_msg(self.position),
            velocity=self.velocity,
            course=self.course,
            safe_zone=[coords_to_ros_msg(xy) for xy in self.safe_zone.exterior.coords],
            model=[coords_to_ros_msg(xy) for xy in self.model.exterior.coords]
        )

    @staticmethod
    def list_to_ros_msg(dynamics: list['DynamicEntity']) -> DynamicEntitiesMsg:
        return DynamicEntitiesMsg(
            dynamics=[dynamic.to_ros_msg() for dynamic in dynamics]
        )

    @classmethod
    def from_ros_msg(cls, ros_msg: DynamicEntityMsg) -> 'DynamicEntity':
        c = object.__new__(cls)
        c.category = ros_msg.category
        c.position = coords_from_ros_msg(ros_msg.position)
        c.point = Point(c.position)
        c.velocity = ros_msg.velocity
        c.course = ros_msg.course
        c.safe_zone = Polygon([coords_from_ros_msg(coords_msg) for coords_msg in ros_msg.safe_zone])
        c.model = Polygon([coords_from_ros_msg(coords_msg) for coords_msg in ros_msg.model])
        return c

    @staticmethod
    def list_from_ros_msg(ros_msg: DynamicEntitiesMsg) -> list['DynamicEntity']:
        return [DynamicEntity.from_ros_msg(dynamic) for dynamic in ros_msg.dynamics]
