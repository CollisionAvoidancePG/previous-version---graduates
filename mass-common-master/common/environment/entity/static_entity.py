from shapely.geometry import Polygon, JOIN_STYLE, CAP_STYLE
from common.ros.msg import (ROSMsgInterface, StaticEntityMsg, StaticEntitiesMsg,
                            coords_to_ros_msg, coords_from_ros_msg)
from common.types import CoordsList
from . import Entity


class StaticEntity(Entity, ROSMsgInterface):
    """Static environment entity that have collision, e.g. land, island"""
    graph: list[list[float]] = None
    model_color: str = 'lightgreen'

    def __init__(self, vertices: CoordsList, safe_zone_size: float):
        safe_zone = Polygon(vertices).buffer(
            distance=2*safe_zone_size,
            single_sided=True,
            join_style=JOIN_STYLE.mitre,
            cap_style=CAP_STYLE.square
        )
        safe_zone = Polygon(safe_zone).simplify(
            tolerance=safe_zone_size,
            preserve_topology=False
        )

        super().__init__(safe_zone, vertices)

    def copy(self) -> "StaticEntity":
        c = object.__new__(StaticEntity)
        c.category = self.category
        c.safe_zone = Polygon(self.safe_zone)
        c.model = Polygon(self.model)
        return c

    def __str__(self) -> str:
        return (f'<b>{self.__class__.__name__}:{self.category}</b><br>'
                f'{len(self.safe_zone.exterior.xy[0]) - 1} vertices<br>'
                f'area {self.safe_zone.area:0.2f} m²')

    def to_ros_msg(self) -> StaticEntityMsg:
        return StaticEntityMsg(
            category=self.category,
            safe_zone=[coords_to_ros_msg(xy) for xy in self.safe_zone.exterior.coords],
            model=[coords_to_ros_msg(xy) for xy in self.model.exterior.coords]
        )

    @staticmethod
    def list_to_ros_msg(statics: list['StaticEntity']) -> StaticEntitiesMsg:
        return StaticEntitiesMsg(
            statics=[static.to_ros_msg() for static in statics]
        )

    @classmethod
    def from_ros_msg(cls, ros_msg: StaticEntityMsg) -> 'StaticEntity':
        c = object.__new__(cls)
        c.category = ros_msg.category
        c.safe_zone = Polygon([coords_from_ros_msg(coords_msg) for coords_msg in ros_msg.safe_zone])
        c.model = Polygon([coords_from_ros_msg(coords_msg) for coords_msg in ros_msg.model])
        return c

    @staticmethod
    def list_from_ros_msg(ros_msg: StaticEntitiesMsg) -> list['StaticEntity']:
        return [StaticEntity.from_ros_msg(static) for static in ros_msg.statics]
