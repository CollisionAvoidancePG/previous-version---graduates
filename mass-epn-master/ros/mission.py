#!/usr/bin/env python3
import rospy

from common import logging
from common.environment import Node, Path, Velocity
from common.units import DD

from common.ros.srv import (
    PATH_SEND_SRV,
    PathSend,
    PathSendRequest
)

NODE_NAME = "mission_node"

log = logging.getLogger(NODE_NAME)


class Mission:

    def __init__(self, path: Path):
        rospy.wait_for_service(PATH_SEND_SRV)
        path_sender = rospy.ServiceProxy(PATH_SEND_SRV, PathSend,
                                         persistent=False)
        status = path_sender(PathSendRequest(path.to_ros_msg()))
        log.info(status)


if __name__ == '__main__':
    rospy.init_node(NODE_NAME)
    path = object.__new__(Path)

    nodes = [Node(DD(54.31990, 18.49807), Velocity.FULL_AHEAD),
             Node(DD(54.31995, 18.49751), Velocity.FULL_AHEAD)]

    object.__setattr__(path, 'nodes', nodes)

    Mission(path)
