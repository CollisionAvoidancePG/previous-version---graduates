from shapely.geometry import LineString

from common.ros.msg import ROSMsgInterface, PathMsg
from common.serialization import Serializable, serialize_list, deserialize_list

from . import Node


FEASIBLE_STR = '<span style="color:green"><b>Feasible</b></span>'
UNFEASIBLE_STR = '<span style="color:red">Unfeasible</span>'


class Path(Serializable, ROSMsgInterface):
    """Ship's path"""
    nodes: list[Node]
    line: LineString
    feasible: bool = None

    def __init__(self, nodes: list[Node]):
        self.nodes = nodes
        self.update()

    def update(self) -> float:
        self.line = LineString([node.position for node in self.nodes])
        for i in range(len(self.nodes) - 1):
            self.nodes[i].index = i
            self.nodes[i].set_course(self.nodes[i+1])
        self.nodes[-1].index = -1

    def copy(self):
        cls = self.__class__
        new = cls([node.copy() for node in self.nodes])
        new.feasible = self.feasible
        return new

    def draw(self, go, fig):
        x, y = self.line.xy
        fig.add_traces(go.Scatter(
            x=list(x),
            y=list(y),
            name=str(self),
            customdata=[str(node) for node in self.nodes],
            hoverlabel={'namelength': 0},
            hovertemplate="%{customdata}",
            opacity=0.6
        ))

    def serialize(self) -> dict:
        return {
            'nodes': serialize_list(self.nodes)
        }

    def deserialize(self, dictionary: dict):
        super().deserialize(dictionary)
        self.nodes = deserialize_list(self.nodes, Node)
        self.update()

    def __repr__(self) -> str:
        return f'Path(length={self.line.length:.2f}m)'

    def __str__(self, insert='') -> str:
        return (
            f'<b>Path</b>{insert}<br>'
            f'{FEASIBLE_STR if self.feasible else UNFEASIBLE_STR}<br>'
            f'Nodes: {len(self.nodes)}<br>'
            f'Length: {self.line.length:.2f}m'
        )

    def to_ros_msg(self) -> PathMsg:
        return PathMsg(
            nodes=[node.to_ros_msg() for node in self.nodes],
            feasible=self.feasible
        )

    @classmethod
    def from_ros_msg(cls, ros_msg: PathMsg) -> 'Path':
        c = cls([Node.from_ros_msg(node) for node in ros_msg.nodes])
        c.feasible = ros_msg.feasible
        return c
