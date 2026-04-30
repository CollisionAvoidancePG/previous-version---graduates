from abc import ABC, abstractmethod
from common.types import Coords

POSITION_MSG = "/mavros/global_position/raw/fix"
VELOCITY_MSG = "/mavros/global_position/gp_vel"
COURSE_MSG = "/mavros/global_position/compass_hdg"
MOTOR_BATTERY_MSG = "/mavros/battery"
JETSON_VOLTAGE_MSG = "/voltage"
RC_STATUS_MSG = "/mavros/3dr_radio/radio_status"

CAMERA_DETECTED_MSG = "/mass/camera/detected"
LIDAR_DETECTED_MSG = "/mass/lidar/detected"
PANEL_VIRTUAL_MSG = "/mass/panel/virtual"
ENVIRONMENT_MSG = "/mass/env"

EPN_STATE_MSG = "/mass/epn/state"
EPN_GLOBAL_PATH_MSG = "/mass/epn/global_path"
EPN_LOCAL_PATH_MSG = "/mass/epn/local_path"


class ROSMsgInterface(ABC):
    @abstractmethod
    def to_ros_msg(self):
        pass

    @classmethod
    @abstractmethod
    def from_ros_msg(cls, ros_msg):
        pass


try:
    from mass_common.msg import (
        CoordsMsg,
        DynamicEntityMsg,
        DynamicEntitiesMsg,
        EnvironmentMsg,
        NodeMsg,
        PathMsg,
        StaticEntityMsg,
        StaticEntitiesMsg
    )
except ImportError:
    class ROSMsg:
        def __repr__(self) -> str:
            return "ROSMsg: " + str(self.__dict__)

        def __str__(self) -> str:
            return self.__repr__()

    class CoordsMsg(ROSMsg):
        pass

    class DynamicEntityMsg(ROSMsg):
        pass

    class DynamicEntitiesMsg(ROSMsg):
        pass

    class EnvironmentMsg(ROSMsg):
        pass

    class NodeMsg(ROSMsg):
        pass

    class PathMsg(ROSMsg):
        pass

    class StaticEntityMsg(ROSMsg):
        pass

    class StaticEntitiesMsg(ROSMsg):
        pass


def coords_to_ros_msg(coords: Coords) -> CoordsMsg:
    return CoordsMsg(
        x=coords[0],
        y=coords[1]
    )


def coords_from_ros_msg(ros_msg: CoordsMsg) -> Coords:
    return Coords(x=ros_msg.x, y=ros_msg.y)
