#!/usr/bin/env python3
import rospy

from common import logging
from common.ros.msg import LIDAR_DETECTED_MSG
from mass_common.msg import StaticEntitiesMsg
from common.units import DD
from common.environment import StaticEntity, detected


NODE_NAME = "lidar_stub_node"

log = logging.getLogger(NODE_NAME)

if __name__ == '__main__':
    rospy.init_node(NODE_NAME)
    pub = rospy.Publisher(LIDAR_DETECTED_MSG, StaticEntitiesMsg, queue_size=0)
    rate = rospy.Rate(10)

    log.info(f'{NODE_NAME} ready')

    while not rospy.is_shutdown():

        msg = []
        msg.append(detected([
            DD(54.35914611174979, 18.51593869526812),
            DD(54.35906501289466, 18.51571004740567),
            DD(54.35913742259442, 18.51540684045764),
            DD(54.35921562492680, 18.51562057650297),
            DD(54.35923589958125, 18.51587407739395)
        ]))
        pub.publish(StaticEntity.list_to_ros_msg(msg))
        rate.sleep()
