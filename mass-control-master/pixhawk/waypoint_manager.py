#!/usr/bin/env python3
import rospy

from common import logging
from common.ros.msg import (
    PathMsg,
    NodeMsg,
    coords_from_ros_msg
)
from common.ros.srv import (
    PATH_SEND_SRV,
    PathSend,
    PathSendResponse
)
from common.units import toDD

from mavros_msgs.msg import Waypoint, CommandCode, WaypointList
from mavros_msgs.srv import WaypointPush, WaypointClear

NODE_NAME = "waypoint_manager_server"

log = logging.getLogger(NODE_NAME)


class WaypointManager:
    def __init__(self):
        rospy.init_node(NODE_NAME)
        self.server = rospy.Service(PATH_SEND_SRV, PathSend, WaypointManager.__path_send_handler)
        log.info("WaypointManager ready")
        WaypointManager.__clear_waypoints()
        rospy.spin()

    @staticmethod
    def __path_send_handler(request):
        log.info("received path")
        wl = pathmsg_to_waypoints(request.path)
        wl[0].is_current = True
        success = WaypointManager.__send_waypoints(wl)
        msg = "sent" if success else "failed to send"
        log.info(msg)
        return PathSendResponse(success)

    @staticmethod
    def __send_waypoints(wl) -> bool:
        try:
            WaypointManager.__clear_waypoints()
            service_name = "mavros/mission/push"
            rospy.wait_for_service(service_name)
            waypoint_sender = rospy.ServiceProxy(service_name, WaypointPush, persistent=True)

            success = waypoint_sender.call(start_index=0, waypoints=wl).success

            return success

        except rospy.ServiceException:
            print("sth")

    @staticmethod
    def __clear_waypoints() -> bool:
        try:
            service_name = "mavros/mission/clear"
            rospy.wait_for_service(service_name)
            waypoint_clearer = rospy.ServiceProxy(service_name, WaypointClear, persistent=False)

            success = waypoint_clearer()

            return success

        except rospy.ServiceException:
            print("sth")


def pathmsg_to_waypoints(path: PathMsg) -> WaypointList:
    return [nodemsg_to_waypoint(node) for node in path.nodes]


def nodemsg_to_waypoint(node: NodeMsg) -> Waypoint:
    waypoint = Waypoint()
    waypoint.frame = Waypoint.FRAME_GLOBAL_REL_ALT
    waypoint.command = CommandCode.NAV_WAYPOINT

    # Hold time
    waypoint.param1 = 0

    # Acceptance radius in meters (if the sphere with this radius is hit,
    # the waypoint counts as reached)
    waypoint.param2 = 0.5

    # 0 to pass through the WP, if > 0 radius to pass by WP.
    # Positive value for clockwise orbit, negative value for
    # counter-clockwise orbit. Allows trajectory control.
    waypoint.param3 = 0

    # Desired yaw angle at waypoint (rotary wing).
    # NaN to use the current system yaw heading mode`
    # (e.g. yaw towards next waypoint, yaw to home, etc.).
    waypoint.param4 = float("NaN")

    waypoint.x_lat, waypoint.y_long = toDD(*coords_from_ros_msg(node.position))
    # TODO: start using node.velocity
    waypoint.is_current = False
    waypoint.autocontinue = True
    return waypoint


if __name__ == '__main__':
    WaypointManager()
