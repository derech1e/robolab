import time
import logging
from typing import Tuple

from odometry import Odometry
from planet import Planet, Direction
from sensors.touch_sensor import TouchSensor
from sensors.speaker_sensor import SpeakerSensor
from sensors.color_sensor import ColorSensor
from enums import StopReason, PathStatus, Color
from sensors.motor_sensor import MotorSensor
from communication import Communication
from driver import Driver


class Robot:

    def __init__(self, client, logger: logging.Logger):
        self.logger = logger

        # ******************************** #
        #  Init sensors                    #
        # ******************************** #
        self.button = TouchSensor()
        self.speaker_sensor = SpeakerSensor()
        self.color_sensor = ColorSensor()
        self.motor_sensor = MotorSensor()

        self.planet = Planet()
        self.communication = Communication(client, logger)
        self.communication.set_robot(self)
        self.odometry = Odometry()
        self.driver = Driver(self.motor_sensor, self.color_sensor)

        self.active = True
        self.planet.group3mode = True

        # Exploration
        self.__start_node: Tuple[Tuple[int, int], Direction] = None
        self.__current_node: Tuple[Tuple[int, int], Direction] = None
        self.__next_node: Tuple[Tuple[int, int], Direction] = None
        # next_node is basically the current_node, but with updated direction.
        # The new direction is the favoured direction, we want to drive to next

        self.target: Tuple[int, int] = None
        self.node_color: Color = None

    def set_target(self, target: Tuple[int, int]):
        self.target = target

    def set_start_node(self, start_x: int, start_y: int, start_direction: Direction):
        self.__start_node = ((start_x, start_y), start_direction)

    def set_current_node(self, end_x: int, end_y: int, end_direction: Direction):
        self.__current_node = ((end_x, end_y), end_direction)

    def update_next_path(self, direction: Direction):
        self.__next_node = ((self.__next_node[0], self.__next_node[1]), direction)

    def is_node_current_target(self, current_position):
        if self.target is None:
            return False

        return current_position[0][0] == self.target[0] and current_position[0][1] == self.target[1]

    def add_path(self, start, target, weight):
        self.planet.add_path(start, target, weight)

    def play_tone(self):
        self.speaker_sensor.play_tone()

    def handle_node(self, current_position: Tuple[Tuple[int, int], Direction], stop_reason: StopReason):
        self.logger.debug("\n\nStart node handling...")

        if stop_reason == StopReason.FIRST_NODE:
            self.logger.debug("Detected the first node")
            self.communication.send_ready()
        else:
            path_status = PathStatus.FREE if not stop_reason == StopReason.COLLISION else PathStatus.BLOCKED
            self.logger.debug(f"Path status: {path_status}")

            # send path message with last driven path
            self.communication.send_path(self.planet.planet_name, self.__start_node, current_position, path_status)

            # Check if target is reached
            if self.is_node_current_target(current_position):
                self.communication.send_target_reached("Target reached!")
                return

        scanned_directions = self.follow.scan_node()
        self.planet.add_unexplored_node(current_position[0], self.node_color, scanned_directions)

        self.logger.debug(f"Scanned directions: {scanned_directions}")

    def handle_next_node(self):
        # if next_node is node, the whole map is explored
        if self.__next_node is None:
            # Whole map explored
            if self.target is None:
                self.logger.debug("No target found")
                self.logger.debug("Init mission ending")
                return True

            path_2_target = self.planet.get_to_target(self.__current_node, self.target)
            if path_2_target is None:
                self.logger.debug("Target is not located on this planet")
                self.logger.debug("Init mission ending")
                # TODO: Check how to send target is not on map
                # Exploration complete
                return True

            self.__next_node = path_2_target

    def robot(self):
        planet_name = input('Enter the test planet name and wait for response (default: Conway):') or "Conway"
        self.communication.send_test_planet(planet_name)
        print("Press button to start exploration")

        while not self.button.is_pressed():
            continue

        # self.color_sensor.calibrate_hls()
        # time.sleep(5)

        self.logger.debug("Starting exploration...")
        while self.active:
            stop_reason = self.driver.follow_line()

            self.node_color = Color(self.color_sensor.get_color_name())
            self.odometry.update_position(self.motor_sensor.motor_positions)
            self.__current_node = self.odometry.get_coordinates()

            self.logger.debug(f"Current position: {self.odometry.get_coordinates()}")
            self.handle_node(self.__current_node, stop_reason)

            # Wait for path unveiled
            self.logger.debug("Wait for path unveiling...")
            time.sleep(3)

            # Handle exploration
            self.__next_node = self.planet.explore_next(self.__current_node[0], self.__current_node[1])
            self.logger.debug(f"Next selected path: {self.__next_node}")

            # Break if target is reached or the whole planet is explored
            if self.handle_next_node():
                break

            self.communication.send_path_select(self.planet.planet_name, self.__next_node)
            self.logger.debug("Wait for path correction...")
            time.sleep(3)

            # Handle direction alignment
            if not stop_reason == StopReason.COLLISION:  # TODO: Improve this remove
                self.motor_sensor.turn_angle_blocking(self.__start_node[1])

        # Mission done
        # TODO: CHECK WHEN WE NEED TO SEND EXPLOR_COMPL OR TARGET_REACHED
        # self.communication.send_exploration_complete("Planet fully discovered!")
