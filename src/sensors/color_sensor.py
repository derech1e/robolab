import colorsys
import json
import math
import time

import ev3dev.ev3 as ev3

from src.enums import Color


class ColorSensor:
    """
    This class is used to control the color sensor. It contains several utility functions get more information about the obtained data.
    """

    def __init__(self):
        """
        Initializes the color sensor and set the measure mode to 'RGB-RAW'.
        Also load default color calibration of a config file.
        """
        self.color_sensor = ev3.ColorSensor()
        self.color_sensor.mode = "RGB-RAW"
        self.color_data = {}
        self.load_color_data()

        # Delay
        self.last_check: int = -1
        self.prev_value: float = math.inf

    def __get_raw(self) -> tuple[float, float, float]:
        """
        Get the raw color of the color sensor with a fixed delay of 25ms
        :return: tuple[float, float, float]
        """
        if self.last_check < time.time_ns() + 25_000_000:  # Add execution delay of 25ms
            self.prev_value = self.color_sensor.raw
            self.last_check = time.time_ns()
        return self.prev_value

    def get_color_hls(self) -> tuple[float, float, float]:
        """
        Returns the color of the color sensor in HLS format
        :return: tuple[float, float, float]
        """
        color = self.__get_raw()
        try:
            return colorsys.rgb_to_hls(color[0], color[1], color[2])
        except ZeroDivisionError:
            return 0, 0, 0

    def get_luminance(self) -> float:
        """
        Returns luminance of the sensor by calling get_color_hls function to get the luminance
        :return: float
        """
        return self.get_color_hls()[1]

    def get_color_name(self) -> Color:
        """
        Returns the color of a node. If no node is detected it returns a NONE color
        :return: Color
        """
        raw_color = self.__get_raw()

        if raw_color[0] > raw_color[1] + raw_color[2]:
            return Color.RED

        if raw_color[0] * 1.6 < raw_color[1] and raw_color[0] * 1.6 < raw_color[2] and raw_color[0] < 70:
            return Color.BLUE

        return Color.NONE

    def is_node(self) -> bool:
        """
        Returns a boolean indicating whether the sensor is detecting a node
        :return: Bool
        """
        color = self.get_color_name()
        return color == Color.BLUE or color == Color.RED

    def load_color_data(self):
        """
        Load the color data into the color_data variable
        :return: Void
        """
        with open("sensors/color_data.json", "r") as data:
            self.color_data = json.load(data)
