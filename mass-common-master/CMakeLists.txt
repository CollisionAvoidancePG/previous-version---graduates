cmake_minimum_required(VERSION 3.0.2)
project(mass_common)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  message_generation
  catkin_virtualenv
  sensor_msgs
)

add_message_files(
  FILES
  CoordsMsg.msg
  DynamicEntitiesMsg.msg
  DynamicEntityMsg.msg
  EnvironmentMsg.msg
  NodeMsg.msg
  PathMsg.msg
  StaticEntitiesMsg.msg
  StaticEntityMsg.msg
)

# Generate services in the 'srv' folder
add_service_files(
  FILES
  DestinationSet.srv
  EnvironmentGet.srv
  PathSend.srv
)

# Generate added messages and services with any dependencies listed here
generate_messages(
  DEPENDENCIES
  std_msgs  # Or other packages containing msgs
)

catkin_package(
 CATKIN_DEPENDS rospy message_runtime
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

install(FILES
  requirements.o
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
