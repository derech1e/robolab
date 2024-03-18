# !/usr/bin/env python3

import math
import csv
import os
import shutil
from planet import Direction, Planet
import constants
from typing import Tuple, List
from enums import Color

from sensors.motor_sensor import MotorSensor


class Odometry:
    def __init__(self, motor_sensor: MotorSensor):
        """
        Initializes odometry module
        """
        self.motor_sensor = motor_sensor
        self.motor_positions = motor_sensor.get_motor_positions()

        self.local_x_coordinate = 0
        self.local_y_coordinate = 0
        self.local_orientation = 0
        self.path = r'../data/'
        self.file_str = "../data/path.csv"

        # create folder for csv data files
        shutil.rmtree(self.path, ignore_errors=True)
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.list_of_coords = []

    @staticmethod
    def __get_diff_in_cm(tu1: Tuple[int, int], tu2: Tuple[int, int]) -> Tuple[float, float]:
        left = (tu1[0] - tu2[0]) * constants.ROT_TO_CM
        right = (tu1[1] - tu2[1]) * constants.ROT_TO_CM * constants.MAGIC_VALUE
        return left, right

    def update_position(self, motor_positions):
        print("------------- UPDATIING POSITION ----------------")

        print(f"Koordinates before: ({self.local_x_coordinate}, "
              f"{self.local_y_coordinate}), Oriantation: {self.local_orientation}")

        for i in range(15, len(motor_positions) - 5):
            dl, dr = self.__get_diff_in_cm(motor_positions[i + 1], motor_positions[i])

            # update orientation
            alpha = (dr - dl) / constants.AXLE_LENGTH
            self.local_orientation += alpha

            # update koordinates
            if dr == dl:
                s = dr
            else:
                s = constants.AXLE_LENGTH * (dr + dl) / (dr - dl) * math.sin((dr - dl) / (2 * constants.AXLE_LENGTH))

            delta_x = s * (-1) * math.sin(self.local_orientation)
            delta_y = s * math.cos(self.local_orientation)

            self.local_x_coordinate += delta_x
            self.local_y_coordinate += delta_y

            self.list_of_coords.append((self.local_x_coordinate, self.local_y_coordinate))

        print(f"Koordinates after: ({self.local_x_coordinate}, "
              f"{self.local_y_coordinate}), Oriantation: {self.local_orientation}")

        with open(self.file_str, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(motor_positions)

    @staticmethod
    def __clip_orientation(rad) -> int:
        return (360 - round(math.degrees(rad) / 90) * 90) % 360

    def get_norm(self, v1:Tuple[float, float], v2: Tuple[float,float]):
        return abs(v2[0]-v1[0]) + abs(v2[1]-v1[1])

    def __clip_coordinat(self, x:float, y:float, color: Color, planet: Planet) -> Tuple[int,int]:
        """
        Function that return the coordinates in the global coordinates. Takes planet and color to snap the coordinates to right colored node.
        """
        floored_x = math.floor(x/50)
        floored_y = math.floor(y/50)

        # check if 
        if(planet.check_node_color((floored_x,floored_y), color)):
            if self.get_norm((floored_x*50, floored_y*50), (x,y)) < self.get_norm((floored_x*50 +50, floored_y*50+50),(x,y)):
                return(floored_x, floored_y)
            else:
                return floored_x + 1, floored_y + 1
        else:
            if self.get_norm((floored_x * 50 + 50, floored_y * 50), (x, y)) < self.get_norm(
                    (floored_x, floored_y * 50 + 50), (x, y)):
                return floored_x + 1, floored_y
            else:
                return floored_x, floored_y + 1

    def set_coordinates(self, position: Tuple[Tuple[int, int], Direction]):
        """
        Set the position of the robot in coordinates from mother ship
        """
        self.local_x_coordinate = position[0][0] * 50
        self.local_y_coordinate = position[0][1] * 50
        self.local_orientation = (360 - position[1].value) % 360 / 180 * math.pi
        print(f"setting coordinates in odo: {self.local_x_coordinate},"
              f"{self.local_y_coordinate}, ori: {self.local_orientation}")
        self.file_str = f"{self.path}{position[0][0]}+{position[0][1]}+{position[1].value}.csv"

    def get_coordinates(self, color: Color, planet: Planet) -> Tuple[Tuple[int, int], Direction]:
        """
        Get the position of the robot in coordinates from mother ship
        """
        # return self.fclip(self.local_x_coordinate, self.local_y_coordinate, self.local_orientation, color, planet)
        # return ((self.__clip_coordinat(self.local_x_coordinate), self.__clip_coordinat(self.local_y_coordinate)),
        #         Direction(self.__clip_orientation(self.local_orientation)))
        return (self.__clip_coordinat(self.local_x_coordinate, self.local_y_coordinate, color, planet), Direction(self.__clip_orientation(self.local_orientation)))
