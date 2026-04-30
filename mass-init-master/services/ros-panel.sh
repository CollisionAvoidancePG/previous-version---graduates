#!/bin/zsh
source /opt/ros/noetic/setup.zsh
source /home/mass/catkin_ws/devel/setup.zsh
source /home/mass/catkin_ws/src/mass-panel/venv/bin/activate
python /home/mass/catkin_ws/src/mass-panel/panel_node.py
