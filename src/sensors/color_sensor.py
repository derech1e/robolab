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
        color = self.cs.raw  # Range: 0-1020
        try:
            color_hls = colorsys.rgb_to_hls(color[0], color[1], color[2])
        except ZeroDivisionError:
            color_hls = (0, 0, 0)
        return color_hls

    def get_hls_color_name(self):
        raw_color = self.get_color_hls()

        # Check for black
        # 0.31666666666666665, 47.0, -0.43478260869565216
        if 0.25 < raw_color[0] < 0.31 and 40 < raw_color[1] < 80 and 0.4 < abs(raw_color[2]) < 0.59:
            return "black"

        # Check for white
        # 0.31583793738489874, 340.5, -0.2665684830633284
        if raw_color[0] < 0.4 and raw_color[1] > 300 and raw_color[2] > -0.4:
            return "white"

        # Check for blue
        # (0.4823717948717949, 90.0, -0.5842696629213483)
        # (0.48381877022653724, 90.5, -0.5754189944134078)
        # (0.5396825396825397, 21.5, -0.5121951219512195)
        # (0.5520833333333334, 17.0, -0.5)
        # (0.5555555555555555, 21.0, -0.75)
        # (0.4597222222222222, 100.0, -0.6060606060606061)
        # (0.4616519174041298, 92.5, -0.6174863387978142)
        # (0.4616519174041298, 93.5, -0.6108108108108108)
        # (0.4605263157894737, 92.0, -0.6263736263736264)
        # (0.46017699115044247, 91.5, -0.6243093922651933)
        # (0.46017699115044247, 91.5, -0.6243093922651933)
        if 0.4 < raw_color[0] < 0.56 and 17 < raw_color[1] < 110 and 0.5 < abs(raw_color[2]) < 0.75:
            return "blue"

        # Check for red
        # (0.03803131991051454, 107.5, -0.6995305164319249)
        # (0.035639412997903554, 101.5, -0.7910447761194029)
        # (0.038854805725971366, 109.5, -0.7511520737327189)
        # (0.02, 100.0, -0.7575757575757576)
        # (0.04320987654320988, 112.0, -0.7297297297297297)
        # (0.04320987654320988, 112.0, -0.7297297297297297)
        # (0.04347826086956522, 111.5, -0.7285067873303167)
        # (0.051656920077972714, 109.5, -0.7880184331797235)
        # (0.048654244306418216, 103.5, -0.7853658536585366)
        # (0.050724637681159424, 103.5, -0.7853658536585366)
        # (0.028606965174129362, 161.0, -0.8375)
        # (0.02832244008714596, 96.5, -0.8010471204188482)
        # (0.026143790849673203, 99.5, -0.7766497461928934)
        # (0.028508771929824556, 109.0, -0.7037037037037037)
        # (0.04718875502008032, 118.0, -0.7094017094017094)

        if 0.02 < raw_color[0] < 0.05 and 90 < raw_color[1] < 170 and 0.68 < abs(raw_color[2]) < 0.86:
            return "red"

        return "black"  # TODO: Check black color range; this default should throw an error

        # if self.color_data["white"][0] - self.ACCEPTANCE_NO_COLOR < raw_color[0] < self.color_data["white"][0] + self.ACCEPTANCE_NO_COLOR:
        #     return False
        # else:
        #     value = self.color_data["blue"]
        #     if value[0] - self.ACCEPTANCE_RANGE < raw_color[0] < value[0] + self.ACCEPTANCE_RANGE:
        #         return "blue"
        #
        #     value = self.color_data["red"]
        #     if value[0] - self.ACCEPTANCE_RANGE < raw_color[0] < value[0] + self.ACCEPTANCE_RANGE:
        #         return "red"
        #     return False

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
