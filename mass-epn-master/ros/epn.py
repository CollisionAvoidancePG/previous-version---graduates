#!/usr/bin/env python3
import rospy

import math

from functools import partial

from common import logging
from common.environment import Node, Velocity, Environment
from common.ros.msg import (
    POSITION_MSG,
    EPN_STATE_MSG,
    EPN_GLOBAL_PATH_MSG,
    EPN_LOCAL_PATH_MSG,
    PathMsg
)
from common.ros.srv import (
    ENVIRONMENT_GET_SRV,
    EPN_DESTINATION_SRV,
    DestinationSet,
    DestinationSetRequest,
    DestinationSetResponse,
    EnvironmentGet,
    EnvironmentGetRequest
)
from common.sm import StateMachine, State
from common.types import Coords
from common.units import DD

from sensor_msgs.msg import NavSatFix
from std_msgs.msg import String

from ga import Population

from ros import Mission

from path import generators, PathChromosome
from common.environment import Path

MAX_NODES = 20

EPN_GLOBAL_RETRIES = 5
EPN_LOCAL_RETRIES = 10

POSITION_DELTA_MAX = 1  # meters
NEXT_NODE_DELTA_MIN = 2  # meters

NODE_NAME = "epn_node"

log = logging.getLogger(NODE_NAME)


def distance(a: Coords, b: Coords) -> float:
    return math.dist(a, b)


class EPN(StateMachine):
    idle = State(initial=True)
    global_epn = State()
    local_epn = State()
    cruising = State()

    destination_published = idle >> global_epn | local_epn >> global_epn | cruising >> global_epn \
        | global_epn >> global_epn
    ga_finished = global_epn >> local_epn | local_epn >> cruising
    destination_achieved = cruising >> idle
    position_delta = cruising >> local_epn

    current_position: Coords = None
    destination: Coords = None
    global_path: Path = None
    global_path_node_id: int = 1

    local_path: Path = None

    environment_getter = None

    def __init__(self):
        super().__init__()
        rospy.init_node(NODE_NAME)
        rospy.wait_for_service(ENVIRONMENT_GET_SRV)
        self.environment_getter = rospy.ServiceProxy(
            ENVIRONMENT_GET_SRV, EnvironmentGet, persistent=False)
        rospy.Subscriber(POSITION_MSG, NavSatFix, self.update_current_position)

        self.state_pub = rospy.Publisher(EPN_STATE_MSG, String, queue_size=0)
        self.global_path_pub = rospy.Publisher(EPN_GLOBAL_PATH_MSG, PathMsg, queue_size=0)
        self.local_path_pub = rospy.Publisher(EPN_LOCAL_PATH_MSG, PathMsg, queue_size=0)

        self.server = rospy.Service(EPN_DESTINATION_SRV, DestinationSet,
                                    self.__destination_set_handler)

        log.info("EPN ready")

    def env(self, with_detection: bool) -> Environment:
        # global epn does calculation only on environment from map
        try:
            response = self.environment_getter(EnvironmentGetRequest(with_detection))
        except ServiceException:
            log.warning("Error getting env from EnvironmentManager")
            return

        if not response.success:
            log.warning("Error getting env from EnvironmentManager")
            return

        return Environment.from_ros_msg(response.env)

    def __destination_set_handler(self, request: DestinationSetRequest) -> DestinationSetResponse:
        log.info(f'Received destination {request.latitude}, {request.longitude}')
        self.global_path = None
        self.global_path_node_id = 1
        self.destination = DD(request.latitude, request.longitude)
        self.destination_published()
        return DestinationSetResponse(True)

    def update_current_position(self, data):
        self.current_position = DD(data.latitude, data.longitude)

    def calculate_population(self, start: Coords, end: Coords, with_detection: bool):
        env = self.env(with_detection)

        bb = env.bounding_box

        path_generator = partial(generators.simplest_random,
                                 start=Node(start, Velocity.HALF_AHEAD),
                                 end=Node(end, Velocity.HALF_AHEAD),
                                 nodes_range=(0, MAX_NODES),
                                 x_range=(bb[0], bb[2]),
                                 y_range=(bb[1], bb[3]))

        path_constructor = partial(PathChromosome,
                                   nodes=[node for node in path_generator()],
                                   environment=env)

        pop = Population(
            size=10,
            constructor=path_constructor,
        )
        pop.run(cost_target=1, max_generations=1000)

        return next(filter(lambda x: x.feasible, pop.chromosomes), None)

    def on_enter_idle(self):
        log.info('idle')
        self.state_pub.publish(self.state.name)

    def on_enter_global_epn(self):
        log.info('GlobalEPN')
        self.state_pub.publish(self.state.name)

        retries = 0
        while self.global_path is None:
            if self.scheduled_transition:
                return
            start = self.current_position
            end = self.destination
            self.global_path = self.calculate_population(start, end, with_detection=False)
            retries += 1
            if retries > EPN_GLOBAL_RETRIES:
                log.error("Could not calculate feasible global path")
                # TODO: Change mode to manual

        self.global_path_pub.publish(self.global_path.to_ros_msg())
        self.local_path = None
        self.ga_finished()

    def on_enter_local_epn(self):
        log.info('LocalEPN')
        self.state_pub.publish(self.state.name)

        end = self.global_path.nodes[self.global_path_node_id].position

        retries = 0
        self.local_path = None
        while self.local_path is None:
            if self.scheduled_transition:
                return
            start = self.current_position
            self.local_path = self.calculate_population(start, end, with_detection=True)
            retries += 1
            if retries > EPN_LOCAL_RETRIES:
                log.error("Could not calculate feasible local path")
                # TODO: Decide what to do on local epn fails

        self.local_path_pub.publish(self.local_path.to_ros_msg())
        self.ga_finished()

    def on_enter_cruising(self):
        log.info('Cruising')
        self.state_pub.publish(self.state.name)

        log.debug(self.local_path)
        Mission(self.local_path)

        while True:
            if self.scheduled_transition:
                return

            if self.global_path_node_id >= len(self.global_path.nodes):
                self.destination_achieved()
                break

            current_position = self.current_position
            start_position = self.local_path.nodes[0].position
            next_global = self.global_path.nodes[self.global_path_node_id].position

            if distance(current_position, next_global) < NEXT_NODE_DELTA_MIN:
                self.global_path_node_id += 1
                self.position_delta()
                break

            if distance(current_position, start_position) > POSITION_DELTA_MAX:
                self.position_delta()
                break


if __name__ == '__main__':
    with EPN():
        rospy.spin()
