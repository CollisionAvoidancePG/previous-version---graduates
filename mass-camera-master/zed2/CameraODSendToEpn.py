#!/usr/bin/env python3
import rospy
import numpy as np
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float64
from geometry_msgs.msg import TwistStamped
from common.environment.entity import DynamicEntity
from common.environment import boat
from common.ros.msg import CAMERA_DETECTED_MSG
from common import logging
from common.units import DD
from common.types import Coords
from mass_common.msg import DynamicEntitiesMsg
from zed_interfaces.msg import ObjectsStamped
# from zed_interfaces.msg import Object

PUB_NODE_NAME = "mass_camera_node"
LISTENER_NODE_NAME = "mass_camera_listener"
CUR_POS_MSG = "/mavros/global_position/raw/fix"  # uncomment for real gps
# CUR_POS_MSG = "/gps"  # uncomment for mock gps
CUR_HDG_MSG = "/mavros/global_position/compass_hdg"
CUR_VEL_MSG = "/mavros/global_position/raw/gps_vel"
ZED2_OD_MSG = "/zed2/zed_node/obj_det/objects"
log = logging.getLogger(PUB_NODE_NAME)

DEFAULT_MODEL = [[-1, -1], [-1, 1], [1, 1], [1, -1]]
DEFAULT_SAFEZONE = [[-2, -2], [-2, 2], [2, 2], [2, -2]]


class Camera():
    current_position: Coords = DD(51.231030, 17.115796)  # spawner żuli
    current_course: float = float(0)
    current_velocity: float = float(0)
    # dynamics: List[DynamicEntity] = []

    def rotate_vector_by_course(self, vector, course, is_deg):
        if is_deg:
            theta = np.deg2rad(self.course_to_rot(course))
        else:
            theta = course
        rot = np.array([[np.cos(theta), -np.sin(theta), 0],
                        [np.sin(theta), np.cos(theta), 0],
                        [0, 0, 1]])
        return np.dot(rot, vector)

    def course_to_rot(self, course):
        return (450-course)%360

    def __init__(self) -> None:
        rospy.init_node(PUB_NODE_NAME)
        self.pub = rospy.Publisher(CAMERA_DETECTED_MSG, DynamicEntitiesMsg, queue_size=0)
        rospy.Subscriber(CUR_POS_MSG, NavSatFix, self.update_current_position)
        rospy.Subscriber(ZED2_OD_MSG, ObjectsStamped, self.update_detected_objects)
        rospy.Subscriber(CUR_HDG_MSG, Float64, self.update_current_course)
        rospy.Subscriber(CUR_VEL_MSG, TwistStamped, self.update_current_velocity)
        rospy.loginfo("ZED2 Camera OD started")
        rospy.spin()

    def update_detected_objects(self, data):
        dynamic_list = []
        for detected in data.objects:
            pos = detected.position
            # pos_xy = Coords(pos[0], pos[1])
            # velocity should be global, not relative to our vessel
            vel_detected = detected.velocity
            vel_self = (0, self.current_velocity, 0)
            vel = np.add(vel_detected, vel_self)

            conf = detected.confidence
            label = detected.label
            self.print_objs(pos, vel, conf, label)
            # TODO relative velocity with our vessel
            vel_norm = np.sqrt(vel[0]*vel[0]+vel[1]*vel[1]+vel[2]*vel[2])
            print(vel_norm)
            # https://www.omnicalculator.com/math/angle-between-two-vectors
            full_ahead_vect = [0, 1, 0]
            # this is different among other coordinate systems
            # https://www.stereolabs.com/docs/positional-tracking/coordinate-frames/

            # acos is 0 to pi - detect if the vessel is going left or right
            # if x component of velocity is negative the vessel goes left
            # the angle is then negative
            # assuming we go always forward no need to change coordinate systems for vel
            LR_course_flag = 1 if vel[0] > 0 else -1
            vel_course = np.arccos(np.dot(full_ahead_vect, vel)/vel_norm)*LR_course_flag

            vel_course_deg = np.rad2deg(vel_course)

            # correct detected vessel position with our course rotation
            pos_corr = self.rotate_vector_by_course(pos, self.current_course, True)
            pos_shift = Coords(pos_corr[0] + self.current_position[0],
                               pos_corr[1] + self.current_position[1])

            dist = np.sqrt(pos_corr[0]*pos_corr[0]+pos_corr[1]*pos_corr[1])
            if (dist < 3.0):
                continue

            dyn = boat(position=pos_shift, velocity=vel_norm, course=vel_course_deg)
            # dynamic_list.append(dyn)
            
            # pos_msg = CoordsMsg(x=pos_shift[0], y=pos_shift[1])
            print(dyn.serialize())
            dynamic_list.append(dyn)
        rospy.loginfo(dynamic_list)
        # dynamic_msg_list = [DynamicEntityMsg(position=dynamic.position,
        # velocity=dynamic.velocity, course=dynamic.course, cls="boat") for dynamic in dynamic_list]
        self.pub.publish(DynamicEntity.list_to_ros_msg(dynamic_list))
        # pub.publish(dynamics)
        rospy.loginfo("CAM OD dynamics published")

    def print_objs(self, pos, vel, conf, label):
        rospy.loginfo(str(conf) + ' ' + label + ' pos: ' + str(pos) + ' vel: ' + str(vel))

    def update_current_position(self, data):
        if np.abs(data.latitude) < 0.01:
            rospy.logwarn("Position is 0, not updating")
            return
        if np.abs(data.longitude) < 0.01:
            rospy.logwarn("Position is 0, not updating")
            return
        self.current_position = DD(data.latitude, data.longitude)
        rospy.loginfo("Position [m]: " + str(self.current_position[0]) + " " +
                      str(self.current_position[1]))
        rospy.loginfo("\tPosition [dd]: " + str(data.latitude) + " " + str(data.longitude))

    def update_current_course(self, data):
        self.current_course = data.data
        rospy.loginfo("Course: " + str(self.current_course))

    def update_current_velocity(self, data):
        # FIXME
        # print(data)
        pass


if __name__ == '__main__':
    try:
        Camera()
    except rospy.ROSInterruptException:
        pass
