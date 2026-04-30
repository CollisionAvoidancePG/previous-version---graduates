cmake_minimum_required(VERSION 3.0.2)
project(mass_epn)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  catkin_virtualenv
  sensor_msgs
)

catkin_package(
 CATKIN_DEPENDS rospy
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

catkin_python_setup()

catkin_install_python(PROGRAMS
  ros/epn.py
  ros/mission.py
  ros/environment_manager.py
  stubs/gps_stub.py
  stubs/lidar_stub.py
  stubs/camera_stub.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(FILES
  requirements.o
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
