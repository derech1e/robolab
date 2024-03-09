import colorsys
import json

import ev3dev.ev3 as ev3


class ColorSensor:
    def __init__(self):
        self.cs = ev3.ColorSensor()
        self.cs.mode = "RGB-RAW"
        self.color_data = {
            "white": (0.1, 0.1, 0.1),
            "black": (0.1, 0.1, 0.1),
            "blue": (0.1, 0.1, 0.1),
            "red": (0.1, 0.1, 0.1),
        }
        self.load_color_data()

        # set the range in which the read value is accepted as a color
        # TODO: das passt so nicht, der wert muss noch veraendert werden
        self.ACCEPTANCE_RANGE = 0.02 
        self.ACCEPTANCE_NO_COLOR = 0.15

    def return_color(self):
        return self.color_data

    # read color Data from file
    def load_color_data(self):
        with open("sensors/color_data.json", "r") as data:
            self.color_data = json.load(data)

    # if we want to use hls
    def get_color_hls(self) -> tuple[float, float, float]:
        color = self.cs.raw
        try:
            color_hls = colorsys.rgb_to_hls(color[0], color[1], color[2])
        except ZeroDivisionError:
            color_hls = (0, 0.1, 0.1)
        return color_hls

    def get_hls_color_name(self):
        raw_color = self.get_color_hls()
        if self.color_data["white"][0] - self.ACCEPTANCE_NO_COLOR < raw_color[0] < self.color_data["white"][0] + self.ACCEPTANCE_NO_COLOR:
            return False
        else:
            value = self.color_data["blue"]
            if value[0] - self.ACCEPTANCE_RANGE < raw_color[0] < value[0] + self.ACCEPTANCE_RANGE:
                return "blue"

            value = self.color_data["red"]
            if value[0] - self.ACCEPTANCE_RANGE < raw_color[0] < value[0] + self.ACCEPTANCE_RANGE:
                return "red"
            return False

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
