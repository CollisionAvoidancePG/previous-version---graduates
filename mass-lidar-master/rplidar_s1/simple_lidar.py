#!/usr/bin/env python3
import rospy
from common.environment import DetectedStaticEntity
from common import converters, logging
from common.types import DD
from mass_common.msg import StaticEntities as StaticEntitiesMsg


NODE_NAME = "simple_lidar_node"
CUR_POS_MSG = "/mavros/global_position/raw/fix"
DETECTED_MSG = "/mass/lidar/detected"


log = logging.getLogger(NODE_NAME)


class SimpleLidar:

    pub: rospy.Publisher = None

    def __init__(self):
        rospy.init_node(NODE_NAME)
        self.pub = rospy.Publisher(DETECTED_MSG, StaticEntitiesMsg, queue_size=0)
        # Subscriber to rplidar msg
        # rospy.Subscriber(msgname, msgdatatype, self.prepare_data)
        log.info('SimpleLidar ready')

    def prepare_data(self, data):
        # convert data from lidar to objects containing vertices in DD coordinate system
        # ...
        # then for example for given vertices
        vertices = []
        vertices.append(DD(54.21326498442491, 17.95486807823181))
        vertices.append(DD(54.21211057065281, 17.95370936393737))
        vertices.append(DD(54.21326498442491, 17.95486807823181))

        detected_list = []
        detected_list.append(DetectedStaticEntity(vertices))
        # detected_list.append(DetectedStaticEntity(Other dtected object vertices))

        self.pub.publish(converters.convert_static_entities_to_msg(detected_list))


if __name__ == '__main__':
    SimpleLidar()
    rate = rospy.Rate(1)
    rate.sleep()
