#!/usr/bin/env python3
import rospy
import time
from sensor_msgs.msg import LaserScan

unlockPause = 0
pub = rospy.Publisher('/scan_filtered', LaserScan, queue_size=10)
name = f"{time.localtime()}.txt"
textFile = open(name, "w")


def callback(data):
    global unlockPause
    msg = data
    tabRanges = []

    for range in msg.ranges:
        # Tutaj będzie jakiś filtr
        tabRanges.append(range)
    msg.ranges = tabRanges

    if (time.localtime().tm_sec < 1):
        textFile.write(str(msg.ranges))
        unlockPause = 1
    elif (unlockPause == 1):
        textFile.write('\n ---- Angle increment ----- \n')
        textFile.write(str(msg.angle_increment))
        textFile.write('\n ---- Table count ----- \n')
        textFile.write(str(len(msg.ranges)))
        textFile.write('\n ---- Time increment ----- \n')
        textFile.write(str(msg.time_increment))
        textFile.write('\n ---- Angle min ----- \n')
        textFile.write(str(msg.angle_min))
        textFile.write('\n ---- Angle max ----- \n')
        textFile.write(str(msg.angle_max))
        textFile.write('\n ---- scan time ----- \n')
        textFile.write(str(msg.scan_time))
        textFile.write('\n ---- range min ----- \n')
        textFile.write(str(msg.range_min))
        textFile.write('\n ---- range max ----- \n')
        textFile.write(str(msg.range_max))
        textFile.write('\n ---- przerwa----- \n')
        unlockPause = 0

    ###########
    pub.publish(msg)


def laser_filter():
    rospy.init_node('laser_filter', anonymous=False)
    rospy.Subscriber("/scan", LaserScan, callback)
    rospy.loginfo("Filter started")
    rospy.spin()


if __name__ == '__main__':
    try:
        laser_filter()
    except rospy.ROSInterruptException:
        pass

textFile.close()
