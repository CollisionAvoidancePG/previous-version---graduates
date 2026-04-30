#!/usr/bin/env python3
import rospy

from common import logging
from common.environment import boat
from common.ros.msg import CAMERA_DETECTED_MSG, DynamicEntitiesMsg
from common.units import DD, deg, mps


NODE_NAME = "camera_stub_node"

log = logging.getLogger(NODE_NAME)

if __name__ == '__main__':
    rospy.init_node(NODE_NAME)
    pub = rospy.Publisher(CAMERA_DETECTED_MSG, DynamicEntitiesMsg, queue_size=0)
    rate = rospy.Rate(10)

    log.info(f'{NODE_NAME} ready')

    while not rospy.is_shutdown():

        pub.publish([boat(
            position=DD(54.35875673069881, 18.51708354461037),
            velocity=1*mps,
            course=270*deg
        )])
        rate.sleep()
