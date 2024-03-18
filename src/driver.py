# imports
import logging
import time

from enums import StopReason, Color
from planet import Direction
from sensors.color_sensor import ColorSensor
from sensors.sonar_sensor import SonarSensor
from sensors.motor_sensor import MotorSensor
from sensors.speaker_sensor import *
from pid import PID
import constants


class Driver:
    """
    This class is responsible the line following and node detection of the robot.
    """

    def __init__(self, motor_sensor: MotorSensor, color_sensor: ColorSensor, speaker_sensor: SpeakerSensor, logger: logging.Logger):
        """
        Initialize the Driver class as well as the pid controller
        """
        self.motor_sensor = motor_sensor
        self.color_sensor = color_sensor
        self.speaker_sensor = speaker_sensor
        self.pid = PID(color_sensor, motor_sensor)
        self.sonar_sensor = SonarSensor()
        self.logger = logger

        self.is_first_node = True

    def turn_find_line(self) -> None:
        """
        Rotate the robot until a line is detected
        :return: void
        """
        while self.color_sensor.get_luminance() > self.color_sensor.average_lightness:
            self.motor_sensor.drive_with_speed(-100, 100)
        self.motor_sensor.stop()
        self.logger.debug("Line found")

        # TODO: if the robot is not on the line, add code for slower turning in opposite direction

    def follow_line(self) -> StopReason:
        """
        function for line following, uses the PID class to follow a line. Returns if an obstacle is found
        :return: StopReason
        """
        self.motor_sensor.reset_position()
        stop_reason = StopReason.NODE

        while True:
            speed = self.pid.calc_speed()
            self.motor_sensor.drive_with_speed(speed[0], speed[1])

            # check for collision
            if self.sonar_sensor.is_colliding():
                self.logger.debug("Collision detected")
                self.motor_sensor.stop()
                self.speaker_sensor.play_tone()

                # turn and find line
                self.motor_sensor.turn_angle(30)
                self.turn_find_line()
                stop_reason = StopReason.COLLISION

            if self.color_sensor.is_node():
                self.logger.debug("Node detected")
                if self.is_first_node:
                    stop_reason = StopReason.FIRST_NODE
                    self.is_first_node = False
                break

        self.motor_sensor.stop()
        return stop_reason

    def rotate_to_line(self, direction: int) -> None:
        """
        Rotate to a direction and finds the line
        :param direction: int
        :return: void
        """

        if direction > 0:
            self.motor_sensor.turn_angle(direction - 20)
            self.turn_find_line()
        else:
            self.turn_find_line()

    def __angle_to_direction(self, angle: int) -> int:
        """
        converts motor positions to an angle
        :param angle: int
        :return: int
        """
        if 0 <= angle <= 160:
            return 0
        elif 160 <= angle <= 290:
            return 270
        elif 290 <= angle <= 420:
            return 180
        elif 420 <= angle < 550:
            return 90

        return 0  # Default

    def scan_node(self) -> list[Direction]:
        """
        turns the rover 360 deg and scans vor paths
        :return: list[Direction]
        """
        self.motor_sensor.stop()
        self.logger.debug("Scanning node...")

        # drive straight to position over the node
        while self.color_sensor.get_color_name() is not Color.NONE:
            self.motor_sensor.drive_with_speed(constants.SPEED, constants.SPEED)
        self.logger.debug(f"Stopped driving: Detected {self.color_sensor.get_color_name()}")

        self.motor_sensor.drive_cm(1.5, 1.5, constants.SPEED)  # Driving a tick further to get the perfect alignment
        self.motor_sensor.turn_angle(-30)  # turn -30 deg to scan first path

        self.motor_sensor.stop()  # Reset motor positions for perfect rotation
        directions = []
        self.motor_sensor.full_turn()  # Do a 360 turn

        while self.motor_sensor.is_running():
            position = self.motor_sensor.get_position()
            luminance = self.color_sensor.get_luminance()

            time.sleep(0.1)

            if luminance < 100:  # Check if the luminance value of the color sensor is lower than 100 and therefor black
                self.logger.debug(f"Detected line at position: {position}")
                direction = Direction(self.__angle_to_direction(position))
                if direction not in directions:
                    directions.append(direction)

        south = Direction.SOUTH  # Default direction is entrance direction
        if south in directions:
            directions.remove(south)
        self.motor_sensor.stop()  # Stop scan maneuver
        return directions
