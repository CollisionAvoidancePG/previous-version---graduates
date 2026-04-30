#!/usr/bin/env python3
import rospy
import numpy as np

from common import logging
from common.environment import StaticEntity, Path, Environment, Node
from common.ros.msg import (
    POSITION_MSG,
    VELOCITY_MSG,
    COURSE_MSG,
    MOTOR_BATTERY_MSG,
    JETSON_VOLTAGE_MSG,
    RC_STATUS_MSG,
    EPN_STATE_MSG,
    EPN_GLOBAL_PATH_MSG,
    EPN_LOCAL_PATH_MSG,
    ENVIRONMENT_MSG,
    PANEL_VIRTUAL_MSG,
    PathMsg,
    EnvironmentMsg,
    StaticEntitiesMsg
)
from common.ros.srv import (
    EPN_DESTINATION_SRV,
    DestinationSet,
    DestinationSetRequest
)
from common.types import Coords
from common.units import DD, toDD, kmph

from panel import app, telemetry

from mavros_msgs.msg import RadioStatus
from sensor_msgs.msg import NavSatFix, BatteryState
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Float32, Float64, String

NODE_NAME = "panel_node"

VESSEL_HISTORY_MAX = 10_000

log = logging.getLogger(NODE_NAME)


class PanelNode:
    virtual_statics: list[StaticEntity] = None

    def __init__(self):
        rospy.init_node(NODE_NAME)

        rospy.Subscriber(POSITION_MSG, NavSatFix, self.__position_handler)
        rospy.Subscriber(VELOCITY_MSG, TwistStamped, self.__velocity_handler)
        rospy.Subscriber(COURSE_MSG, Float64, self.__course_handler)
        rospy.Subscriber(MOTOR_BATTERY_MSG, BatteryState, self.__motor_battery_handler)
        rospy.Subscriber(JETSON_VOLTAGE_MSG, Float32, self.__jetson_voltage_handler)
        rospy.Subscriber(RC_STATUS_MSG, RadioStatus, self.__radio_status_handler)
        rospy.Subscriber(EPN_STATE_MSG, String, self.__epn_state_handler)
        rospy.Subscriber(EPN_GLOBAL_PATH_MSG, PathMsg, self.__epn_global_path_handler)
        rospy.Subscriber(EPN_LOCAL_PATH_MSG, PathMsg, self.__epn_local_path_handler)
        rospy.Subscriber(ENVIRONMENT_MSG, EnvironmentMsg, self.__environment_handler)

        self.destination_setter = rospy.ServiceProxy(
            EPN_DESTINATION_SRV, DestinationSet, persistent=False)
        self.virtual_static_pub = rospy.Publisher(
            PANEL_VIRTUAL_MSG, StaticEntitiesMsg, queue_size=0)

        self.virtual_static_remove_all()

        telemetry.on('destination_set', self.destination_set)
        telemetry.on('vessel_history_clear', self.vessel_history_clear)
        telemetry.on('virtual_static_place', self.virtual_static_place)
        telemetry.on('virtual_static_remove_all', self.virtual_static_remove_all)

        log.info('Starting Flask server')
        app.run(host="0.0.0.0", port=5123)
        log.info('Flask server started')

        log.info("Panel node ready")
        rospy.spin()

    def __position_handler(self, msg: NavSatFix):
        telemetry.vessel.position = DD(msg.latitude, msg.longitude)
        node = Node(telemetry.vessel.position, 0)
        if telemetry.vessel_history is None:
            telemetry.vessel_history = Path([node, node])
        else:
            telemetry.vessel_history.nodes.append(node)
        
        # clear old history
        if len(telemetry.vessel_history.nodes) > VESSEL_HISTORY_MAX:
            telemetry.vessel_history.nodes.pop(0)

    def __velocity_handler(self, msg: TwistStamped):
        v = np.array([msg.twist.linear.x, msg.twist.linear.y, msg.twist.linear.z])
        telemetry.vessel.velocity = np.linalg.norm(v) * kmph

    def __course_handler(self, msg: Float64):
        telemetry.vessel.course = msg.data

    def __motor_battery_handler(self, msg: BatteryState):
        telemetry.pixhawk.voltage = msg.voltage

    def __jetson_voltage_handler(self, msg: Float32):
        telemetry.jetson.voltage = msg.data

    def __radio_status_handler(self, msg: RadioStatus):
        telemetry.remote.signal = msg.rssi_dbm

    def __environment_handler(self, msg: EnvironmentMsg):
        telemetry.env = Environment.from_ros_msg(msg)

    def __epn_state_handler(self, msg: String):
        telemetry.epn.state = msg.data

    def __epn_global_path_handler(self, msg: PathMsg):
        telemetry.epn.global_path = Path.from_ros_msg(msg)

    def __epn_local_path_handler(self, msg: PathMsg):
        telemetry.epn.local_path = Path.from_ros_msg(msg)

    def destination_set(self, coords: Coords):
        telemetry.epn.destination = coords
        lat, long = toDD(*coords)
        response = self.destination_setter(DestinationSetRequest(latitude=lat, longitude=long))
        if response:
            log.info("Destination set successfully")
        else:
            log.error("Failed to set destination")

    def vessel_history_clear(self):
        telemetry.vessel_history.nodes.clear()

    def virtual_static_publish(self):
        self.virtual_static_pub.publish(StaticEntity.list_to_ros_msg(self.virtual_statics))

    def virtual_static_place(self, static: StaticEntity):
        self.virtual_statics.append(static)
        self.virtual_static_publish()

    def virtual_static_remove_all(self):
        self.virtual_statics = []
        self.virtual_static_publish()


if __name__ == '__main__':
    PanelNode()
