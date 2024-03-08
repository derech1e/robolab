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

        # set the range in which the read value is accepted as a color
        self.acceptance_range = (0.2, 10, .2)

    def return_color(self):
        return self.color_data

    # read color Data from file
    def load_color_data(self):
        with open("sensors/color_data.json", "r") as data:
            self.color_data = json.load(data)

    # if we want to use hls
    def get_color_HLS(self) -> tuple[float, float, float]:
        color = self.cs.raw
        try:
            color_HLS = colorsys.rgb_to_hls(color[0], color[1], color[2])
        except Exception as e:
            color_HLS = (0.1, 0.1, 0.1)
        return color_HLS

    def check_color_HLS(self):
        raw_color = self.get_color_HLS()
        if(
            self.color_data["white"][0] - 0.05
            < raw_color[0]
            < self.color_data["white"][0] + 0.05
        ):
            return False
        else:
            value = self.color_data["blue"]
            if (
                value[0] - self.acceptance_range[0]
                < raw_color[0]
                < value[0] + self.acceptance_range[0]
            ):
                return "blue"

            value = self.color_data["red"]
            if (
                value[0] - self.acceptance_range[0]
                < raw_color[0]
                < value[0] + self.acceptance_range[0]
            ):
                return "red"
            return False


    # save color Data to file
    def calibrate_HLS(self):
        # read white, read black, read blue, read red
        print("calibrating...")

        for color, _ in self.color_data.items():
            input(f"put the rover on {color}")
            self.color_data[color] = self.get_color_HLS()
            print(self.get_color_HLS())

        with open("sensors/color_data.json", "w") as dataFile:
            json.dump(self.color_data, dataFile)

        print("calibration completed")
