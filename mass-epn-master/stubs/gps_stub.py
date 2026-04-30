#!/usr/bin/env python3
import rospy

from common import logging
from common.ros.msg import POSITION_MSG
from sensor_msgs.msg import NavSatFix

NODE_NAME = "gps_stub_node"

log = logging.getLogger(NODE_NAME)

if __name__ == '__main__':
    rospy.init_node(NODE_NAME)
    pub = rospy.Publisher(POSITION_MSG, NavSatFix, queue_size=0)
    rate = rospy.Rate(10)

    log.info("GPS ready")

    while not rospy.is_shutdown():
        msg = NavSatFix()
        msg.latitude = 54.35923
        msg.longitude = 18.51503
        pub.publish(msg)
        rate.sleep()
