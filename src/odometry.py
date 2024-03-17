# !/usr/bin/env python3

import math
import csv
import os, shutil
from planet import *
import constants

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
        self.file_str = "path.csv"

        #create folder for csv data files
        shutil.rmtree(r'./data')
        newpath = r'./data' 
        if not os.path.exists(newpath):
            os.makedirs(newpath)


        self.list_of_coords = []

    def __get_diff_in_cm(self, tu1: Tuple[int, int], tu2: Tuple[int, int]) -> Tuple[float, float]:
        left = (tu1[0] - tu2[0]) * constants.ROT_TO_CM * constants.MAGIC_VALUE
        right = (tu1[1] - tu2[1]) * constants.ROT_TO_CM / constants.MAGIC_VALUE
        return left, right

    def update_position(self, motor_positions):
        for i in range(8, len(motor_positions) - 8):
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

        # print(f"x = {self.local_x_coordinate}, y = {self.local_y_coordinate}, a = {self.local_orientation}")
        # print(self.local_orientation)
        with open(self.file_str, 'w', newline='') as file:
            writer = csv.writer(file)
            # writer.writerow(['x', 'y'])
            writer.writerows(motor_positions)
            # writer.writerows(self.list_of_coords)

        print(f"Koordinates: ({self.local_x_coordinate}, {self.local_y_coordinate}), Oriantation: {self.local_orientation}")

    def __clip_orientation(self, rad) -> int:
        return (360 - round(math.degrees(rad) / 90) * 90) % 360

    # TODO: clipp to color
    def __clip_coordinat(self, x: float) -> int:
        return round(x / 50)

    def set_coordinates(self, position: Tuple[Tuple[int, int], Direction]):
        """
        Set the position of the robot in coordinates from mother ship
        """
        self.local_x_coordinate = position[0][0] * 50
        self.local_y_coordinate = position[0][1] * 50
        self.local_orientation = (360 - position[1].value)%360 / 180 * math.pi
        print(f"setting coordinates in odo: {self.local_x_coordinate}, {self.local_y_coordinate}, ori: {self.local_orientation}")
        self.file_str = f"data/{position[0][0]}+{position[0][1]}+{position[1].value}.csv"


    def get_coordinates(self) -> Tuple[Tuple[int, int], Direction]:
        """
        Get the position of the robot in coordinates from mother ship
        """
        return ((self.__clip_coordinat(self.local_x_coordinate),
                 self.__clip_coordinat(self.local_y_coordinate)),
                Direction(self.__clip_orientation(self.local_orientation)))
