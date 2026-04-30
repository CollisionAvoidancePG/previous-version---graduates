#!/usr/bin/env python3

# import rospy
import rospy
# import numpy as np
# import open3d as o3d
from sensor_msgs.msg import Image  # , PointCloud2, PointField
from stereo_msgs.msg import DisparityImage
# import sensor_msgs.point_cloud2 as pc2
from cv_bridge import CvBridge, CvBridgeError
from zed_interfaces.msg import ObjectsStamped as Objs
# from zed_interfaces.msg import Object as Obj
from sensor_msgs.msg import NavSatFix as Pos
from sensor_msgs.msg import NavSatStatus as PosStat
# from mass_common.units import DD
import cv2
# import ctypes
# import struct

bridge = CvBridge()


class CamNode:
    position = 0, 0  # lat long alt
    obstacles = []
    satellites_visible = 0

    def fix_callback(self, data: Pos):
        rospy.loginfo("fix callback")
        if data.status.status == PosStat.STATUS_NO_FIX:
            rospy.loginfo("GPS Fix is down, tracking obstacles via camera is unavailable")
        else:
            position = data.latitude, data.longitude
            # update_obstacles()
            rospy.loginfo("GPS OK pos = " + position)

    def get_position(self):
        rospy.init_node('mass_camera_location_listener', anonymous=False)
        rospy.loginfo('mass camera get position')
        while True:
            try:
                fix = rospy.wait_for_message('mavros/global_position/global', Pos, timeout=None)
                self.fix_callback(fix)
            except rospy.exceptions.ROSInterruptException:
                break
        # rospy.Subscriber('mavros/global_position/', Pos, self.fix_callback)
        rospy.spin()

    def save_image(self, image, type, time):
        rospy.loginfo("recv image, " + type + " " + image.encoding)
        try:
           if type == "stereo_rect_color":
               cv2_img = bridge.imgmsg_to_cv2(image, "bgr8")
           else:
               cv2_img = bridge.imgmsg_to_cv2(image, "passthrough")
               cv2_img2 = cv2.normalize(cv2_img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8U)
        except CvBridgeError as e:
           print(e)
        except rospy.exceptions.ROSInterruptException:
           raise
        else:
           if type == "stereo_rect_color":
               cv2.imwrite('output/cam_'+type+str(time)+'.png', cv2_img)
           else:
               cv2.imwrite('output/cam_'+type+str(time)+'.tif', cv2_img2)

    def print_objs(self, objs: Objs):
        print("obj_det")
        for detected in objs.objects:
            pos = str(detected.position)
            vel = str(detected.velocity)
            print(str(detected.confidence) + ' ' + detected.label + ' pos: ' + pos + ' vel: ' + vel)
        pass

    def listener(self):
        rospy.init_node('mass_zed2_node', anonymous=False)
        while True:
            try:
                now = str(rospy.get_time())
                # depth_registered = rospy.wait_for_message(
                #    "zed2/zed_node/depth/depth_registered", Image, timeout=None)
                objcts = rospy.wait_for_message("zed2/zed_node/obj_det/objects", Objs, timeout=None)
                self.print_objs(objcts)
                print(now)
                stereo_rect = rospy.wait_for_message(
                   "zed2/zed_node/stereo/image_rect_color", Image, timeout=None)
                confidence = rospy.wait_for_message(
                   "zed2/zed_node/confidence/confidence_map", Image, timeout=None)
                disparity = rospy.wait_for_message(
                   "zed2/zed_node/disparity/disparity_image", DisparityImage, timeout=None)
                # point_cloud = rospy.wait_for_message("
                # zed2/zed_node/point_cloud/cloud_registered", PointCloud2,
                # timeout=None)
                self.save_image(stereo_rect, "stereo_rect_color_", now)
                # save_image(depth_registered, "depth_float32_", now)
                self.save_image(confidence, "confidence_", now)
                self.save_image(disparity.image, "disparity_", now)
                rospy.loginfo("disp "+str(disparity.max_disparity)+" "+str(disparity.min_disparity)+" "+str(disparity.f)+" "+str(disparity.T))
                # save_pointcloud(point_cloud, "pointcloud_", now)
                # rospy.sleep(3.)
            except rospy.exceptions.ROSInterruptException:
                break
        rospy.spin()


if __name__ == "__main__":
    rospy.loginfo("mass_camera starting")
    a = CamNode()
    # a.get_position()
    a.listener()
