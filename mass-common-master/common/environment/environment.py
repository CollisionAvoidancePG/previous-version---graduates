import sys

from common.ros.msg import ROSMsgInterface, EnvironmentMsg
from common.serialization import Serializable, serialize_list, deserialize_list
from common.types import BoundingBox

from .entity import Entity, StaticEntity, DynamicEntity


def bounding_box(entities: list[Entity]) -> BoundingBox:
    """Calculates maximal bounding box of passed entities."""
    xmin = sys.float_info.max
    ymin = sys.float_info.max
    xmax = sys.float_info.min
    ymax = sys.float_info.min

    for entity in entities:
        bb = entity.safe_zone.bounds
        xmin = min(xmin, bb[0])
        ymin = min(ymin, bb[1])
        xmax = max(xmax, bb[2])
        ymax = max(ymax, bb[3])

    return xmin, ymin, xmax, ymax


class Environment(Serializable, ROSMsgInterface):
    """Environment contains static and dynamic entities"""
    statics: list[StaticEntity]
    dynamics: list[DynamicEntity]

    def __init__(self, statics: list[StaticEntity], dynamics: list[DynamicEntity]):
        self.statics = statics
        self.dynamics = dynamics

    def copy(self) -> "Environment":
        return Environment(
            statics=[static.copy() for static in self.statics],
            dynamics=[dynamic.copy() for dynamic in self.dynamics]
        )

    def serialize(self) -> dict:
        return {
            "statics": serialize_list(self.statics),
            "dynamics": serialize_list(self.dynamics)
        }

    def deserialize(self, dictionary: dict):
        super().deserialize(dictionary)
        self.statics = deserialize_list(self.statics, StaticEntity)
        self.dynamics = deserialize_list(self.dynamics, DynamicEntity)

    @property
    def bounding_box(self) -> BoundingBox:
        return bounding_box(self.statics)

    def draw(self, go, fig):
        """Draw environment on plot"""
        fig.layout.plot_bgcolor = 'white'
        xmin, ymin, xmax, ymax = self.bounding_box
        fig.add_traces(go.Scatter(
            x=[xmin, xmax, xmax, xmin],
            y=[ymin, ymin, ymax, ymax],
            showlegend=False,
            fill="toself",
            fillcolor='lightblue',
            opacity=1,
            mode='none',
            hoverinfo='skip'
        ))

        for i in self.statics + self.dynamics:
            i.draw(go, fig)

    def __str__(self) -> str:
        return ('Environment('
                f'statics={len(self.statics)}, '
                f'dynamics={len(self.dynamics)})')

    def to_ros_msg(self) -> EnvironmentMsg:
        return EnvironmentMsg(
            statics=StaticEntity.list_to_ros_msg(self.statics),
            dynamics=DynamicEntity.list_to_ros_msg(self.dynamics)
        )

    @classmethod
    def from_ros_msg(cls, ros_msg: EnvironmentMsg) -> 'Environment':
        c = object.__new__(cls)
        c.statics = StaticEntity.list_from_ros_msg(ros_msg.statics)
        c.dynamics = DynamicEntity.list_from_ros_msg(ros_msg.dynamics)
        return c
