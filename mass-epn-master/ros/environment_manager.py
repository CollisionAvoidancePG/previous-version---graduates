#!/usr/bin/env python3
import rospy

from common import logging
from common.environment import Environment
from common.environment.entity import DynamicEntity, StaticEntity
from common.ros.msg import (
    POSITION_MSG,
    CAMERA_DETECTED_MSG,
    LIDAR_DETECTED_MSG,
    PANEL_VIRTUAL_MSG,
    ENVIRONMENT_MSG,
    StaticEntitiesMsg,
    DynamicEntitiesMsg,
    EnvironmentMsg
)
from common.ros.srv import (
    ENVIRONMENT_GET_SRV,
    EnvironmentGet,
    EnvironmentGetRequest,
    EnvironmentGetResponse
)
from common.units import DD
from osm import OSMSupplier

from sensor_msgs.msg import NavSatFix

NODE_NAME = "environment_manager_node"

log = logging.getLogger(NODE_NAME)


class EnvironmentManager:

    __map: Environment = None
    detected_statics: list[StaticEntity] = None
    virtual_statics: list[StaticEntity] = None
    detected_dynamics: list[DynamicEntity] = None

    def __init__(self):
        rospy.init_node(NODE_NAME)

        self.server = rospy.Service(ENVIRONMENT_GET_SRV, EnvironmentGet, self.__env_get_handler)
        rospy.Subscriber(CAMERA_DETECTED_MSG, DynamicEntitiesMsg, self.__camera_callback)
        rospy.Subscriber(LIDAR_DETECTED_MSG, StaticEntitiesMsg, self.__lidar_callback)
        rospy.Subscriber(PANEL_VIRTUAL_MSG, StaticEntitiesMsg, self.__virtual_static_callback)
        self.env_pub = rospy.Publisher(ENVIRONMENT_MSG, EnvironmentMsg, queue_size=0)

        self.virtual_statics = []
        self.detected_statics = []
        self.detected_dynamics = []

        log.info("EnvironmentManager ready")
        rospy.spin()

    def __env_get_handler(self, request: EnvironmentGetRequest) -> EnvironmentGetResponse:
        log.info("Received request for new Environment")
        if request.with_detection:
            env = Environment.to_ros_msg(self.map_with_detected)
        else:
            env = Environment.to_ros_msg(self.map)

        self.publish()
        return EnvironmentGetResponse(success=True, env=env)

    def publish(self, force=False):
        self.env_pub.publish(Environment.to_ros_msg(self.map_with_detected))

    def __camera_callback(self, msg):
        log.debug("Received data from camera")
        if msg.dynamics is not None:
            self.detected_dynamics = DynamicEntity.list_from_ros_msg(msg)
        self.publish()

    def __lidar_callback(self, msg):
        log.debug("Received data from lidar")
        if msg.statics is not None:
            self.detected_statics = StaticEntity.list_from_ros_msg(msg)
        self.publish()

    def __virtual_static_callback(self, msg):
        log.info("Received virtual static")
        if msg.statics is not None:
            self.virtual_statics = StaticEntity.list_from_ros_msg(msg)
        self.publish()

    @property
    def map(self) -> Environment:
        if self.__map is None:
            current_position = rospy.wait_for_message(POSITION_MSG, NavSatFix)
            statics = OSMSupplier(DD(current_position.latitude, current_position.longitude),
                                  viewing_dist=150).get_entities()
            self.__map = Environment(statics=statics, dynamics=[])
        map = self.__map.copy()
        map.statics.extend(self.virtual_statics)
        return map

    @property
    def map_with_detected(self) -> Environment:
        map_with_detected = self.map

        # Make copies of detected entities, so they do not change during Environment preparation
        map_with_detected.dynamics = [dynamic.copy() for dynamic in self.detected_dynamics]
        detected_statics = [static.copy() for static in self.detected_statics]

        # TODO: Remove detected_statics that are intersected with detected_dynamics
        map_with_detected.statics.extend(detected_statics)

        return map_with_detected


if __name__ == '__main__':
    EnvironmentManager()
