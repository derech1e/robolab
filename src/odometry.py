# !/usr/bin/env python3

import math
import csv
import os, shutil
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

    def __get_diff_in_cm(self, tu1: Tuple[int, int], tu2: Tuple[int, int]) -> Tuple[float, float]:
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


    def __clip_orientation(self, rad) -> int:
        return (360 - round(math.degrees(rad) / 90) * 90) % 360

    # TODO: clipp to color
    def __clip_coordinat(self, x: float) -> int:
        return round(x / 50)

    def fclip(self, x: float, y: float, rad: float, color: Color, planet: Planet) -> Tuple[Tuple[int, int], Direction]:
        round_x: int = round(x / 50)
        round_y: int = round(y / 50)
        coords: List[Tuple[int, int]] = []
        if planet.check_node_color((round_x, round_y), color):
            return (round_x, round_y), Direction(self.__clip_orientation(rad))
        else:
            x_diff = abs(x - round_x)
            y_diff = abs(y - round_y)
            coords.append(self.round_other_way(x, y, x_diff > y_diff))
            coords.append(self.round_other_way(x, y, not (x_diff > y_diff)))

        c1: bool = coords[0] in planet.paths.keys()
        c2: bool = coords[1] in planet.paths.keys()

        if c2 and not c1:
            return coords[1], Direction(self.__clip_orientation(rad))
        else:
            return coords[0], Direction(self.__clip_orientation(rad))

    @staticmethod
    def round_other_way(x: float, y: float, rounding_x: bool) -> Tuple[int, int]:
        round_x: int = round(x / 50)
        round_y: int = round(y / 50)
        if rounding_x:
            if round_x > x:
                return math.floor(x / 50), round_y
            else:
                return math.ceil(x / 50), round_y

        else:
            if round_y > y:
                return round_x, math.floor(y / 50)
            else:
                return round_x, math.ceil(y / 50)

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

    def get_coordinates(self, planet: Planet, color: Color) -> Tuple[Tuple[int, int], Direction]:
        """
        Get the position of the robot in coordinates from mother ship
        """
        return self.fclip(self.local_x_coordinate, self.local_y_coordinate, self.local_orientation, color, planet)
        # return ((self.__clip_coordinat(self.local_x_coordinate), self.__clip_coordinat(self.local_y_coordinate)),
                # Direction(self.__clip_orientation(self.local_orientation)))
