import logging
import math

import ev3dev.ev3 as ev3

from src import constants


class MotorSensor:
    """
    This class is used to control the motor sensor. It contains several utility functions fundamentally control the movement of the robot
    """

    def __init__(self, logger: logging.Logger):
        """
        Initializes motor sensor module and init motors
        :param logger: The logger of the program
        """
        self.logger = logger
        self.motor_left = ev3.LargeMotor("outB")
        self.motor_left.reset()
        self.motor_left.stop_action = "hold"

        self.motor_right = ev3.LargeMotor("outC")
        self.motor_right.reset()
        self.motor_right.stop_action = "hold"

        self.motor_positions = [(self.motor_left.position, self.motor_right.position)]  # Init the motor_positions with the current motor positions
        # self.counter: int = 0

    def get_position(self) -> float:
        """
        Get the average motor position of both the left and the right motor
        :return: float
        """
        return (abs(self.motor_left.position) + abs(self.motor_right.position)) / 2

    def __update_speed(self, motor: ev3.LargeMotor, speed: int) -> None:
        """
        Update the speed of a specific motor with the 'run-forward' command
        :param motor: ev3.LargeMotor
        :param speed: int
        :return: Void
        """
        motor.speed_sp = speed
        motor.command = "run-forever"

    def __update_speed_position_relative(self, motor: ev3.LargeMotor, position: int, speed: int) -> None:
        """
        Update the speed of a specific motor with a relative position in the 'run-to-rel-pos' command
        :param motor: ev3.LargeMotor
        :param position: int
        :param speed: int
        :return: Void
        """
        motor.position_sp = position
        motor.speed_sp = speed
        motor.command = "run-to-rel-pos"

    def turn_angle(self, angle: int) -> None:
        """
        Turn the robot around the center to a specified angle
        :param angle: int
        :return: Void
        """
        if angle == 0:
            return

        angle = math.radians(angle)
        self.logger.debug(f"Turning to angle: {angle}")

        position_old = (self.motor_left.position, self.motor_right.position)

        alpha = 0
        turn_speed = 100 * (1 if angle > 0 else -1)

        # Do until angle is reached
        while abs(alpha) < abs(angle):
            self.drive_with_speed(-turn_speed, turn_speed)
            position_new = (self.motor_left.position, self.motor_right.position)
            delta_pos = (position_new[0] - position_old[0], position_new[1] - position_old[1])
            alpha = alpha + (delta_pos[1] - delta_pos[0]) / 9.5 * 0.05
            position_old = position_new
        self.stop()

    def full_turn(self) -> None:
        """
        Do a full turn maneuver (360-degree turn) with relative positions
        :return: Void
        """
        self.__update_speed_position_relative(self.motor_left, -600, 150)
        self.__update_speed_position_relative(self.motor_right, 600, 150)

    def drive_cm(self, cm_left: float, cm_right: float, speed: int) -> None:
        """
        Drive a specific centimeters distance and a given speed. This action is blocking.
        :param cm_left: float
        :param cm_right: float
        :param speed: int
        :return: Void
        """
        self.motor_right.position_sp = cm_right / constants.ROT_TO_CM
        self.motor_left.position_sp = cm_left / constants.ROT_TO_CM

        self.motor_right.speed_sp = speed
        self.motor_left.speed_sp = speed

        self.motor_right.command = "run-to-rel-pos"
        self.motor_left.command = "run-to-rel-pos"

        self.motor_left.wait_until_not_moving()

    def drive_with_speed(self, speed_left: int, speed_right: int) -> None:
        """
        Apply a speed to the left and the right motors. The speed runs both motors until there are stopped.
        :param speed_left: int
        :param speed_right: int
        :return: Void
        """

        # only append every 3rd time
        # self.counter += 1
        # if self.counter > 3:
        self.motor_positions.append((self.motor_left.position, self.motor_right.position))

        self.__update_speed(self.motor_left, speed_left)
        self.__update_speed(self.motor_right, speed_right)

    def is_running(self) -> bool:
        """
        Return if the left or the right motor is currently running
        :return: Bool
        """
        return self.motor_right.is_running or self.motor_left.is_running

    def stop(self) -> None:
        """
        Stop the left and the right motor and reset both motor positions
        :return: Void
        """
        self.motor_left.stop()
        self.motor_right.stop()
        self.motor_right.reset()
        self.motor_right.stop_action = "hold"
        self.motor_left.reset()
        self.motor_left.stop_action = "hold"

    def reset_position(self):
        """
        Reset the motor positions of the left and the right motor. Clear the motor position array for the odometry.
        :return: Void
        """
        self.motor_left.reset()
        self.motor_right.reset()
        self.motor_positions = []

    def beyblade(self, speed):
        """
        Beyblade beyblade LET IT GOOOOOOO
        """
        self.__update_speed(self.motor_left, -speed)
        self.__update_speed(self.motor_right, speed)
        return self.motor_left.position, self.motor_right.position
