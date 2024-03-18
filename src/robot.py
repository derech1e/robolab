import time
import logging
from typing import Tuple, Optional

import constants
from odometry import Odometry
from planet import Planet, Direction
from driver import Driver
from enums import StopReason, PathStatus, Color
from sensors.control_button import ControlButton
from sensors.speaker_sensor import SpeakerSensor
from sensors.color_sensor import ColorSensor
from sensors.motor_sensor import MotorSensor


class Robot:

    def __init__(self, communication, logger: logging.Logger):
        self.logger = logger

        # ******************************** #
        #  Init sensors                    #
        # ******************************** #
        self.control_button = ControlButton()
        self.speaker_sensor = SpeakerSensor()
        self.color_sensor = ColorSensor()
        self.motor_sensor = MotorSensor()

        self.planet = Planet()
        self.communication = communication
        self.communication.set_robot(self)
        self.odometry = Odometry(self.motor_sensor, self.logger)
        self.driver = Driver(self.motor_sensor, self.color_sensor, self.speaker_sensor, self.logger)
        self.active = True

        # Exploration
        self.__start_node: Tuple[Tuple[int, int], Direction] = ((0, 0), Direction.NORTH)
        self.__current_node: Tuple[Tuple[int, int], Direction] = None
        self.__next_node: Tuple[Tuple[int, int], Direction] = None
        # next_node is basically the current_node, but with updated direction.
        # The new direction is the favoured direction, we want to drive to next

        self.target: Tuple[int, int] = None
        self.node_color: Color = None
        self.node_counter = 0
        self.last_received_message = -1

    def reset_message_timer(self):
        self.last_received_message = time.time_ns()

    def wait_for_message(self):
        while self.last_received_message + 3 * 1_000_000_000 > time.time_ns():
            time.sleep(0.1)  # Sleep until next check

    def set_target(self, target: Tuple[int, int]):
        self.target = target

    def set_start_node(self, start_node: Tuple[Tuple[int, int], Direction]):
        self.__start_node = start_node

    def set_current_node(self, current_node: Tuple[Tuple[int, int], Direction]):
        self.__current_node = current_node

    def update_next_path(self, direction: Direction):
        self.__next_node = ((self.__next_node[0][0], self.__next_node[0][1]), direction)

    def is_node_current_target(self, current_position):
        if self.target is None:
            return False

        return current_position[0][0] == self.target[0] and current_position[0][1] == self.target[1]

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        self.planet.add_path(start, target, weight)

    def play_tone(self):
        self.speaker_sensor.play_tone()

    def handle_node(self, stop_reason: StopReason) -> Optional[bool]:
        self.node_counter += 1
        self.logger.debug(f"\n**************Node - {self.node_counter}****************\n")
        self.logger.debug("Start node handling...")

        self.node_color = Color(self.color_sensor.get_color_name())
        self.odometry.update_position(self.motor_sensor.motor_positions)
        self.__current_node = self.odometry.get_coordinates(self.node_color, self.planet)
        # odometry sends current looking direction, current node is entry direction
        self.__current_node = (self.__current_node[0], Direction((self.__current_node[1] + 180) % 360))

        if stop_reason == StopReason.FIRST_NODE:
            self.logger.debug("Detected the first node")
            self.communication.send_ready()
        else:
            path_status = PathStatus.FREE if not stop_reason == StopReason.COLLISION else PathStatus.BLOCKED
            self.logger.debug(f"Path status: {path_status}")

            # send path message with last driven path
            if path_status == PathStatus.FREE:
                planet_current_node = self.planet.paths[self.__start_node[0]][self.__start_node[1]]
                if planet_current_node[0] is not None:
                    self.communication.send_path(self.planet.planet_name, self.__start_node, (planet_current_node[0], planet_current_node[1]), path_status)
                else:
                    self.communication.send_path(self.planet.planet_name, self.__start_node, self.__current_node, path_status)
            else:
                self.communication.send_path(self.planet.planet_name, self.__start_node, self.__start_node, path_status)

            self.wait_for_message()

            # Check if target is reached
            if self.is_node_current_target(self.__start_node):
                self.communication.send_target_reached("Target reached!")
                self.wait_for_message()  # Wait for done message
                return True

        self.logger.debug("Wait for path correction...")
        self.wait_for_message()

        self.logger.debug(f"Should we scan path?: {self.__start_node[0] not in self.planet.nodes.keys()}")

        if self.__start_node[0] not in self.planet.nodes.keys():
            scanned_directions = self.driver.scan_node()
            # convert from relative to absolute orientation
            scanned_directions = [Direction((direction + self.__start_node[1]) % 360) for direction in scanned_directions]
            self.planet.add_unexplored_node(self.__current_node[0], self.node_color, scanned_directions)
            self.logger.debug(f"Scanned direction: {scanned_directions}")
        else:
            while self.color_sensor.get_color_name():
                self.motor_sensor.drive_with_speed(constants.SPEED, constants.SPEED)
            self.motor_sensor.drive_cm(1.5, 1.5, constants.SPEED)

    def handle_exploration(self) -> bool:
        self.__next_node = self.planet.get_next_node(self.__start_node, self.target)

        if self.__next_node is None:
            self.logger.debug("Ending mission")
            # Break if target is reached or the whole planet is explored
            self.communication.send_exploration_complete("Exploration Complete!")
            self.wait_for_message()
            return True

        # Send selected path
        self.communication.send_path_select(self.planet.planet_name, self.__next_node)
        self.logger.debug("Wait for path correction...")
        self.wait_for_message()

        # Handle direction alignment
        turn_angle = (self.__start_node[1].value - self.__next_node[1].value) % 360
        self.logger.debug(f"Turning to angle: {turn_angle}")

        self.driver.rotate_to_line(turn_angle)
        self.driver.turn_find_line()
        self.__start_node = self.__next_node

    def robot(self):
        self.logger.info("Press button to start exploration")
        # self.control_button.wait_for_input() # TODO: Continue implementation
        self.logger.debug("Starting exploration...")

        while self.active:
            stop_reason = self.driver.follow_line()
            self.logger.debug(f"Stop reason: {stop_reason}")

            if self.handle_node(stop_reason):
                print("Finished exploration")
                break

            # Wait for path unveiled
            self.logger.debug("Wait for path unveiling...")
            self.wait_for_message()

            # Handle exploration
            if self.handle_exploration():
                break

            # Updating odometry
            self.logger.debug(f"setting odometry to {self.__start_node}")
            self.odometry.set_coordinates(self.__start_node)

        self.logger.info("Mission complete. Ending program...")
