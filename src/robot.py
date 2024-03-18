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
    """
    Class to primary control the robot.
    """

    def __init__(self, communication, logger: logging.Logger):
        """
        Initialize the robot with all needed sensors and other classes.
        """
        self.logger = logger

        # ******************************** #
        #  Init sensors                    #
        # ******************************** #
        self.control_button = ControlButton()
        self.speaker_sensor = SpeakerSensor()
        self.color_sensor = ColorSensor()
        self.motor_sensor = MotorSensor(logger)

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
        """
        Reset the message timer to the current time
        :return: void
        """
        self.last_received_message = time.time_ns()

    def wait_for_message(self):
        """
        Wait three seconds for the next message and block during waiting
        :return: void
        """
        while self.last_received_message + 3 * 1_000_000_000 > time.time_ns():
            time.sleep(0.1)  # Sleep until next check

    def set_target(self, target: Tuple[int, int]):
        """
        Set the current target position
        :param target: Tuple[int, int]
        :return: void
        """
        self.target = target

    def set_start_node(self, start_node: Tuple[Tuple[int, int], Direction]):
        """
        Set the start node used for the next node handling
        :param start_node: Tuple[Tuple[int, int], Direction]
        :return: void
        """
        self.__start_node = start_node

    def set_current_node(self, current_node: Tuple[Tuple[int, int], Direction]):
        """
        Set the current node used for the next node handling
        :param current_node: Tuple[Tuple[int, int], Direction]
        :return: void
        """
        self.__current_node = current_node

    def update_next_path(self, direction: Direction):
        """
        Update the direction of the next node
        :param direction: Direction
        :return: void
        """
        self.__next_node = ((self.__next_node[0][0], self.__next_node[0][1]), direction)

    def is_node_current_target(self, current_position):
        """
        Check if the current node is the target
        :param current_position: Tuple[Tuple[int, int], Direction]
        :return: Bool
        """
        if self.target is None:
            return False

        return current_position[0][0] == self.target[0] and current_position[0][1] == self.target[1]

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction], weight: int):
        """
        Add a path to the planet
        :param start: Tuple[Tuple[int, int], Direction]
        :param target: Tuple[Tuple[int, int], Direction]
        :param weight: int
        :return: Void
        """
        self.planet.add_path(start, target, weight)

    def play_tone(self):
        """
        Play a tone on the speaker sensor
        :return: Void
        """
        self.speaker_sensor.play_tone()

    def handle_node(self, stop_reason: StopReason) -> Optional[bool]:
        """
        Handle the node logic. Based on the stop reason the node handling differs from each other.
        :param stop_reason: StopReason
        :return: Optional[bool]
        """

        self.node_counter += 1
        self.logger.debug(f"\n**************Node - {self.node_counter}****************\n")
        self.logger.debug("Start node handling...")

        self.node_color = self.color_sensor.get_color_name()
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

            # Wait for response of path message
            self.wait_for_message()

            # Check if target is reached
            if self.is_node_current_target(self.__start_node):
                self.communication.send_target_reached("Target reached!")
                self.wait_for_message()  # Wait for done message
                return True

        # Wait for path correction
        self.logger.debug("Wait for path correction...")
        self.wait_for_message()

        self.logger.debug(f"Should we scan path?: {self.__start_node[0] not in self.planet.nodes.keys()}")

        # Check if we need to scan the node
        if self.__start_node[0] not in self.planet.nodes.keys():
            scanned_directions = self.driver.scan_node()
            # convert from relative to absolute orientation
            scanned_directions = [Direction((direction + self.__start_node[1]) % 360) for direction in scanned_directions]
            self.planet.add_unexplored_node(self.__current_node[0], self.node_color, scanned_directions)
            self.logger.debug(f"Scanned direction: {scanned_directions}")
        else:
            while self.color_sensor.get_color_name() is not Color.NONE:
                self.motor_sensor.drive_with_speed(constants.SPEED, constants.SPEED)
            self.motor_sensor.drive_cm(1.5, 1.5, constants.SPEED)

    def handle_exploration(self) -> bool:
        """
        Handle the decision of the path selection. If the target is reached we end the mission. Otherwise, we send the path select message
        and drive the next path.
        :return: Bool
        """
        self.__next_node = self.planet.get_next_node(self.__start_node, self.target)

        if self.__next_node is None:
            self.logger.debug("Ending mission")
            # Break if target is reached or the whole planet is explored
            self.communication.send_exploration_complete("Exploration Complete!")
            self.wait_for_message()
            return True

        # Send selected path
        self.communication.send_path_select(self.planet.planet_name, self.__next_node)
        self.logger.debug("Wait for path select correction...")
        self.wait_for_message()  # Wait for path select correction

        # Handle direction alignment
        turn_angle = (self.__start_node[1].value - self.__next_node[1].value) % 360
        self.logger.debug(f"Turning to angle: {turn_angle}")

        self.driver.rotate_to_line(turn_angle)  # Turn approximately to the selected path
        self.driver.turn_find_line() # Turn until we find a line and can continue following
        self.__start_node = self.__next_node

    def robot(self):
        """
        Handle the whole robot runtime logic.
        :return: Void
        """
        self.logger.debug("Press button to start")
        self.control_button.wait_for_input()
        self.logger.debug("Starting exploration...")

        while self.active:
            # Follow line until we stop
            stop_reason = self.driver.follow_line()
            self.logger.debug(f"Stop reason: {stop_reason}")

            # Handle node if we stop
            if self.handle_node(stop_reason):
                self.logger.debug("Finished exploration")
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

            # play tone for successful communication
            self.play_tone()

        self.logger.info("Mission complete. Ending program...")
