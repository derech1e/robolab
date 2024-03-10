# !/usr/bin/env python3

import math
from typing import Tuple, List

from sensors.motor_sensor import MotorSensor


class Odometry:
    def __init__(self):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        self.AXLE_LENGTH = 10
        self.WHEEL_RADIUS = 5.54 / 2
        self.ROT_TO_CM = 0.0494  #needs fixing

        self.motor_sensor = MotorSensor()
        self.motor_positions = self.motor_sensor.get_motor_positions()
        self.local_coordinates:List[float]

        self.local_x_coordinat = 0
        self.local_y_coordinat = 0
        self.local_oriantation = 0

    def __get_diff_in_cm(self, tu1:Tuple[int,int], tu2:Tuple[int,int]) -> Tuple[float, float]:
        return((tu1[0]-tu2[0]) * self.ROT_TO_CM, (tu1[1]-tu2[1]) * self.ROT_TO_CM)

    def update_position(self, motor_positions):
        for i in range(0, len(motor_positions)-1):
            dl, dr = self.__get_diff_in_cm(motor_positions[i+1], motor_positions[i])

            #update oriantation
            alpha = (dr - dl) / self.AXLE_LENGTH
            self.local_oriantation += alpha

            #update koordinates
            if not dr == dl:
                s = self.AXLE_LENGTH * (dr + dl) / (dr - dl) * math.sin((dr - dl) / (2 * self.AXLE_LENGTH))
                delta_x = s * (-1) * math.sin(self.local_oriantation)
                delta_y = s * math.cos(self.local_oriantation)
                self.local_x_coordinat += delta_x
                self.local_y_coordinat += delta_y


        # print(f"Koordinates: ({self.local_x_coordinat}, {self.local_y_coordinat}), Oriantation: {self.local_oriantation}")
            


    def __radian_to_angle(self, rad):
        return rad / math.pi * 180
        

    def set_coordinates(self, x: int, y: int, angle: float):
        """
        Set the position of the robot in coordinates from muther shipp
        """
        pass

    def get_coordinates(self) -> Tuple[int, int, float]:
        """
        Get the position of the robot in coordinates from muther shipp
        """
        return (self.local_coordinates[0], self.local_coordinates[1], self.__radian_to_angle(self.local_oriantation))

