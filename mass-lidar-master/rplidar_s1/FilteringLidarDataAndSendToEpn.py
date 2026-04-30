
#!/usr/bin/env python3
import rospy
import math
import numpy as np
from sensor_msgs.msg import LaserScan, NavSatFix
from common.environment.entity import StaticEntity, detected
from common import logging
from common.ros.msg import LIDAR_DETECTED_MSG
from common.units import DD
from common.types import Coords
from mass_common.msg import StaticEntitiesMsg
from std_msgs.msg import Float64
NODE_NAME = "simple_lidar_node"
CUR_POS_MSG = "/mavros/global_position/raw/fix"
CUR_ROT_MSG = "/mavros/global_position/compass_hdg"
log = logging.getLogger(NODE_NAME)

#


class Lidar():
    current_position: Coords = None
    list_of_lists_to_compare = []
    list_of_current_rotation = []
    measurements_without_detected_object: float = 0
    current_rotation: float = 0
    
    def __init__(self) -> None:
        self.pub = rospy.Publisher(LIDAR_DETECTED_MSG, StaticEntitiesMsg, queue_size=0)
        rospy.init_node('laser_filter', anonymous=False)
        rospy.Subscriber(CUR_POS_MSG, NavSatFix, self.update_current_position)
        rospy.Subscriber(CUR_ROT_MSG, Float64, self.update_current_rotation)
        rospy.Subscriber("/scan", LaserScan, self.callback)
        rospy.loginfo("Filter started")
        rospy.spin()


    #Lidar starts with -180 degree
    def CalculatePoints(self, radius, angleOfMeasurement):
        y = radius * math.cos(angleOfMeasurement)
        x = radius * math.sin(angleOfMeasurement)
        return Coords(y, x)
    

    def CalculateCoordsFromGpsAndLidar(self, point, position):
        y = point[0] + position[0]
        x = point[1] + position[1]
        return Coords(y, x)
    

    def callback(self, data):
        msg = data
        listOfPointLists = []
        pointList = []
        lastRadius = 0
        numberOfWrongMeasurements = 0
        angleOfMeasurement = math.radians(self.current_rotation) +90
        increseOfMeasurementAngle = msg.angle_increment
        position = self.current_position
        self.measurements_without_detected_object += 1

        for radius in msg.ranges:
            #Several inf measurements in a row should contribute to the closure of the detected object
            if (radius == float("inf")):    #Inf measurements should be ignored     
                numberOfWrongMeasurements += 1
                angleOfMeasurement += increseOfMeasurementAngle
                continue

            if (float(radius) < 2): #Too small measurements should be ignored
                numberOfWrongMeasurements += 1
                angleOfMeasurement += increseOfMeasurementAngle
                continue

            #Distance between actual and latest radius is calculate to determine if object was ended
            if (lastRadius > 0):
                distanceBetweenPoints = math.fabs(float(radius) - float(lastRadius))
            else:
                distanceBetweenPoints = 0

            #If distance between two points in row are smaller than 1m, new object should be stared or actual object should continue  
            if (distanceBetweenPoints < 0.5):
                if (len(pointList) == 0):
                    additionPoint = self.CalculatePoints(float(radius) + 1, angleOfMeasurement)
                    pointList.append(self.CalculateCoordsFromGpsAndLidar(additionPoint, position))
                p1 = self.CalculatePoints(float(radius), angleOfMeasurement)
                pointList.append(self.CalculateCoordsFromGpsAndLidar(p1, position))
            #If distance between two points in row are bigger than 1m, object should ended
            #If there was 5 or more wrong measurements in row, object should end as well
            elif (distanceBetweenPoints > 0.5 or numberOfWrongMeasurements >= 2):
                additionPoint = self.CalculatePoints(float(lastRadius) + 1, angleOfMeasurement)
                pointList.append(self.CalculateCoordsFromGpsAndLidar(additionPoint, position))
                if (len(pointList) > 7):
                    listOfPointLists.append(detected(pointList.copy()))
                    radius = 0
                pointList.clear()

            lastRadius = radius
            numberOfWrongMeasurements = 0 
            angleOfMeasurement += increseOfMeasurementAngle

        self.list_of_lists_to_compare.append(listOfPointLists.copy())
        self.list_of_current_rotation.append(self.current_rotation)
        listOfPointLists.clear()

        if(len(self.list_of_lists_to_compare) == 10):
            evaluation_of_rotations = {i: 0 for i in range(10)}
            number_of_actual_rotation = 0

            #Creating evaluation of current rotation in measurements
            #Only measurements with a rotation similar to other measurements will be considered
            for rotation in self.list_of_current_rotation:
                number_of_actual_rotation += 1
                for additional_rotation in  self.list_of_current_rotation:
                    if(additional_rotation - 5 < rotation < additional_rotation + 5):
                        evaluation_of_rotations[number_of_actual_rotation - 1] += 1
            self.list_of_current_rotation.clear()

            #Creating evaluation of measurements
            #Newest measurement with highest simillar to other measurement will be considered
            max_number_of_similar_not_empty_measurements = 0
            number_of_actual_list = 0
            highest_value_of_intersects_count = 0
            best_measurement = []
            for list_of_point_lists in self.list_of_lists_to_compare:
                number_of_actual_list += 1
                if(evaluation_of_rotations[number_of_actual_list - 1] < 5):
                    continue
                intersects_count = 0
                number_of_similar_measurements = 0
                number_of_actual_additional_list = 0
                for additional_list_of_point_lists in self.list_of_lists_to_compare:
                    number_of_actual_additional_list += 1
                    if(evaluation_of_rotations[number_of_actual_additional_list - 1] < 5):
                        continue
                    
                    if (len(additional_list_of_point_lists) - 5 < len(list_of_point_lists) < len(additional_list_of_point_lists) + 5):
                        number_of_similar_measurements += 1
                        for i in range(0, len(list_of_point_lists) - 1):
                            for j in range(-5, 5):
                                if((i + j) >= 0 and (i + j) < len(additional_list_of_point_lists) - 1):
                                    if(list_of_point_lists[i].model.intersects(additional_list_of_point_lists[i + j].model)):
                                        intersects_count += 1
                                        break
                    if(number_of_similar_measurements >= max_number_of_similar_not_empty_measurements):
                        max_number_of_similar_not_empty_measurements = number_of_similar_measurements
                    if (intersects_count >= highest_value_of_intersects_count):
                        highest_value_of_intersects_count = intersects_count
                        best_measurement = list_of_point_lists.copy()
                        log.info(f'Best measurement was selected')
                        log.info(f'{increseOfMeasurementAngle} increse of measurement angle') 

            #Creating list of object, detected in more than 3 measurements.
            list_of_point_lists_To_Send = []
            if(max_number_of_similar_not_empty_measurements > 3):
                for best_object in best_measurement:
                    intersects_count = 0
                    for list_of_point_lists in self.list_of_lists_to_compare:
                        for object in list_of_point_lists:
                            if(best_object.model.intersects(object.model)):
                                intersects_count += 1
                                break
                        if(intersects_count > 7):
                            log.info(f'Object was added') 
                            list_of_point_lists_To_Send.append(best_object.copy())
                            break

            if(len(list_of_point_lists_To_Send) > 0):
                log.info(f'Measurements without detected object: {self.measurements_without_detected_object}')
                self.measurements_without_detected_object = 0
                self.pub.publish(StaticEntity.list_to_ros_msg(list_of_point_lists_To_Send.copy()))
                log.info(f'{NODE_NAME} ready')

            self.list_of_lists_to_compare.clear()

        if(self.measurements_without_detected_object > 1200):
            log.info(f'{NODE_NAME} Clearing lidar')
            self.measurements_without_detected_object = 0
            self.pub.publish(StaticEntity.list_to_ros_msg([]))
            
        ###########
    def update_current_position(self, data):
        if np.abs(data.latitude) < 0.01:
            rospy.logwarn("Position is 0, not updating")
            return
        if np.abs(data.longitude) < 0.01:
            rospy.logwarn("Position is 0, not updating")
            return
        self.current_position = DD(data.latitude, data.longitude)
        
    def update_current_rotation(self, data):
        self.current_rotation = data.data

if __name__ == '__main__':
    try:
        Lidar()
    except rospy.ROSInterruptException:
        pass
