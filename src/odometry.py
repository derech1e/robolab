# !/usr/bin/env python3

import math
import csv
from typing import Tuple, List
from planet import *

from sensors.motor_sensor import MotorSensor


class Odometry:
    def __init__(self):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        self.AXLE_LENGTH = 10 
        self.WHEEL_RADIUS = 5.54 / 2
        self.ROT_TO_CM = 0.04884  #needs fixing
        self.MAGIC_VALUE = 0.9945

        self.motor_sensor = MotorSensor()
        self.motor_positions = self.motor_sensor.get_motor_positions()
        self.local_coordinates:List[float]

        self.local_x_coordinat = 0
        self.local_y_coordinat = 0
        self.local_oriantation = 0

        self.list_of_coords = []

    def __get_diff_in_cm(self, tu1:Tuple[int,int], tu2:Tuple[int,int]) -> Tuple[float, float]:
        return((tu1[0]-tu2[0]) * self.ROT_TO_CM * self.MAGIC_VALUE, (tu1[1]-tu2[1]) * self.ROT_TO_CM / self.MAGIC_VALUE)

    def update_position(self, motor_positions):
        for i in range(0, len(motor_positions)-1):
            dl, dr = self.__get_diff_in_cm(motor_positions[i+1], motor_positions[i])

            #update oriantation
            alpha = (dr - dl) / self.AXLE_LENGTH
            self.local_oriantation += alpha

            #update koordinates
            if dr == dl:
                s = dr
            else: 
                s = self.AXLE_LENGTH * (dr + dl) / (dr - dl) * math.sin((dr - dl) / (2 * self.AXLE_LENGTH))

            delta_x = s * (-1) * math.sin(self.local_oriantation)
            delta_y = s * math.cos(self.local_oriantation)
            self.local_x_coordinat += delta_x
            self.local_y_coordinat += delta_y


            self.list_of_coords.append((self.local_x_coordinat, self.local_y_coordinat))

        # print(self.local_oriantation)
        with open('path.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            # writer.writerow(['x', 'y'])
            writer.writerows(motor_positions)
            # writer.writerows(self.list_of_coords)

        print(f"Koordinates: ({self.local_x_coordinat}, {self.local_y_coordinat}), Oriantation: {self.local_oriantation}")
            


    def __clip_orientation(self, rad) -> int:
        return (360-round(math.degrees(rad)/90)*90) % 360

    def __clip_coordinat(self, x:float) -> int:
        return round (x / 50)

    def set_coordinates(self, x: int, y: int, angle: float):
        """
        Set the position of the robot in coordinates from muther shipp
        """
        self.local_x_coordinat = x * 50
        self.local_y_coordinat = y * 50
        self.local_oriantation = 360 - angle / 180 * math.pi

        pass

    def get_coordinates(self) -> Tuple[Tuple[int,int], Direction]:
        """
        Get the position of the robot in coordinates from muther shipp
        """
        return ((self.__clip_coordinat(self.local_x_coordinat), self.__clip_coordinat(self.local_y_coordinat)), Direction(self.__clip_orientation(self.local_oriantation)))

