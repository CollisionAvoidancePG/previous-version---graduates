cmake_minimum_required(VERSION 3.0.2)
project(mass_camera)

find_package(catkin REQUIRED COMPONENTS
  rospy
  catkin_virtualenv
)

catkin_package(
  CATKIN_DEPENDS
  rospy
  zed_interfaces
  std_msgs
  sensor_msgs
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_generate_virtualenv(
  INPUT_REQUIREMENTS requirements.txt
  PYTHON_INTERPRETER python3.9
  USE_SYSTEM_PACKAGES TRUE
)

catkin_install_python(PROGRAMS
  zed2/mass_camera.py
  zed2/CameraODSendToEpn.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(FILES
  requirements.o
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
