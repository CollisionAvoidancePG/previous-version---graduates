#!/bin/zsh

mkdir -p ~/.config/pip
cp pip.conf ~/.config/pip

sudo apt install \
python3.9 \
python3.9-venv \
python3-catkin-tools \
ros-noetic-catkin-virtualenv \
python3-vcstool \
ros-noetic-mavros \
ros-noetic-mavros-extras

mkdir -p src

catkin build -j1

cd src

vcs import --recursive < ../repos.yml

cd ..

rosdep install --from-paths src --ignore-src -r -y

# apply camera patch
git apply --reject --whitespace=fix camera.patch

catkin build -j1
