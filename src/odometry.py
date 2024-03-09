# !/usr/bin/env python3

import math

from sensors.motor_sensor import MotorSensor


class Odometry:
    def __init__(self):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        self.AXLE_LENGTH = 0
        self.WHEEL_RADIUS = 0
        self.ROT_TO_CM = 0.1

        self.motor_sensor = MotorSensor()
        self.motor_positions = self.motor_sensor.get_motor_positions()
        self.local_koordinates = (0, 0)
        self.local_orientation = 0

        #convert position data to distance driven per position
        # self.delta_positions_cm = [(self.motor_positions[i][j]-self.motor_positions[i][j]) * self.ROT_TO_CM for i in range(0,len(self.motor_positions)) for j in range(0,1)]


    def __update_orientation(self):
        #convert motor positions to cm
        # self.local_orientations = self.delta_positions_cm[(self.delta_positions_cm[i][1] - self.delta_positions_cm[i][0]) / self.AXLE_LENGTH for i in range(0,len(self.motor_positions))]
        pass

    def __update_position(self):
        pass

    def __radian_to_angle(self):
        pass

    def set_koordinates(self, x: int, y: int, angle: float):
        """
        Set the position of the robot in coordinates from muther shipp
        """
        pass

    def get_koordinates(self) -> tuple[int, int, float]:
        """
        Get the position of the robot in coordinates from muther shipp
        """
        return (0, 0, 0)

