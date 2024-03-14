import colorsys
import json

import ev3dev.ev3 as ev3


class ColorSensor:
    def __init__(self):
        self.cs = ev3.ColorSensor()
        self.cs.mode = "RGB-RAW"
        self.color_data = {}
        self.load_color_data()

        # set the range in which the read value is accepted as a color
        # TODO: das passt so nicht, der wert muss noch veraendert werden
        self.ACCEPTANCE_RANGE_COLOR = 0.08  # smaler if accept color wrongly
        self.ACCEPTANCE_RANGE_NOT_COLOR = 0.05
        self.NO_COLOR = (self.color_data["white"][0] + self.color_data["black"][0]) / 2
        self.AVR_LIGHTNESS = (self.color_data["white"][1] + self.color_data["black"][1]) / 2

    # if we want to use hls
    def get_color_hls(self) -> tuple[float, float, float]:
        color = self.cs.raw
        try:
            color_hls = colorsys.rgb_to_hls(color[0], color[1], color[2])
        except ZeroDivisionError:
            color_hls = (0, 0.1, 0.1)
        return color_hls

    def get_luminance(self):
        return self.get_color_hls()[1]

    def get_brightness_error(self):
        return self.AVR_LIGHTNESS - self.get_luminance()

    # needs to be rewritten
    def get_color_name(self):
        raw_color = self.get_color_hls()
        if 0.288 < raw_color[0] < 0.322: 
            if self.AVR_LIGHTNESS > raw_color[1]:
                return "black"
            else:
                return "white"
        else:
            value = self.color_data["blue"]
            if value[0] - self.ACCEPTANCE_RANGE_COLOR < raw_color[0] < value[0] + self.ACCEPTANCE_RANGE_COLOR:
                return "blue"

            value = self.color_data["red"]
            if value[0] - self.ACCEPTANCE_RANGE_COLOR < raw_color[0] < value[0] + self.ACCEPTANCE_RANGE_COLOR:
                return "red"

            if self.AVR_LIGHTNESS > raw_color[1]:
                return "white"
            else:
                return "black"

    def is_color(self):
        pass

    def is_node(self):
        color = self.get_color_name()
        return color == "blue" or color == "red"

    # save color Data to file
    def calibrate_hls(self):
        # read white, read black, read blue, read red
        print("calibrating...")

        for color, _ in self.color_data.items():
            input(f"put the rover on {color}")
            self.color_data[color] = self.get_color_hls()
            print(self.get_color_hls())

        with open("sensors/color_data.json", "w") as dataFile:
            json.dump(self.color_data, dataFile)

        print("calibration completed")

    # read color Data from file
    def load_color_data(self):
        with open("sensors/color_data.json", "r") as data:
            self.color_data = json.load(data)
