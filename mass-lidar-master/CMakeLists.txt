cmake_minimum_required(VERSION 3.0.2)
project(mass_lidar)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  catkin_virtualenv
  rplidar_ros
)

catkin_package(
 CATKIN_DEPENDS rospy rplidar_ros std_msgs
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_generate_virtualenv(
  INPUT_REQUIREMENTS requirements.txt
  PYTHON_INTERPRETER python3.9
  USE_SYSTEM_PACKAGES FALSE
  ISOLATE_REQUIREMENTS TRUE
)

catkin_install_python(PROGRAMS
  rplidar_s1/RPLidarDataToFile.py
  rplidar_s1/simple_lidar.py
  rplidar_s1/FilteringLidarDataAndSendToEpn.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(FILES
  requirements.o
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
