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
        self.ACCEPTANCE_RANGE_COLOR = 0.1  # smaler if accept color wrongly
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

        # Check for black
        if 0.25 < raw_color[0] < 0.31 and 40 < raw_color[1] < 80 and 0.4 < abs(raw_color[2]) < 0.59:
            return "black"

        # Check for white
        if raw_color[0] < 0.4 and raw_color[1] > 300 and raw_color[2] > -0.4:
            return "white"

        # Check for blue
        if 0.4 < raw_color[0] < 0.56 and 17 < raw_color[1] < 110 and 0.5 < abs(raw_color[2]) < 0.75:
            return "blue"

        # Check for red

        if 0.02 < raw_color[0] < 0.05 and 90 < raw_color[1] < 170 and 0.68 < abs(raw_color[2]) < 0.86:
            return "red"

        return "black"  # TODO: Check black color range; this default should throw an error

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
