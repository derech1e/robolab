import ev3dev.ev3 as ev3
import json


class Sensors:
    def __init__(self):
        self.cs = ev3.ColorSensor()
        self.cs.mode = "RGB-RAW"
        self.colorData = {"white": (0, 0, 0), "black": (0, 0, 0), "blue": (0, 0, 0), "red": (0, 0, 0, 0)}

        # set the range in which the read value is accepted as a color
        self.acceptanceRange = (10, 10, 10)

    # returns the color read by the sensor (R,G,B) 1020
    def get_color(self):  # ->tuple[int,int,int]
        return self.cs.raw

    def check_color(self):
        # TODO: schoener machen evtl anderer farbraum
        raw_color = self.cs.raw

        value = self.colorData["blue"]
        if value[0] - self.acceptanceRange[0] < raw_color[0] < value[0] + self.acceptanceRange[0]:
            if value[1] - self.acceptanceRange[1] < raw_color[1] < value[1] + self.acceptanceRange[1]:
                if value[2] - self.acceptanceRange[2] < raw_color[2] < value[2] + self.acceptanceRange[2]:
                    return "blue"

        value = self.colorData["red"]
        if value[0] - self.acceptanceRange[0] < raw_color[0] < value[0] + self.acceptanceRange[0]:
            if value[1] - self.acceptanceRange[1] < raw_color[1] < value[1] + self.acceptanceRange[1]:
                if value[2] - self.acceptanceRange[2] < raw_color[2] < value[2] + self.acceptanceRange[2]:
                    return "red"
        return False

    # read color Data from file
    def load_color_data(self):
        with open("resources/colorData.json", "r") as data:
            self.colorData = json.load(data)

    # save color Data to file
    def calibrate(self):
        # read white, read black, read blue, read red
        print("calibrating...")

        for color, value in self.colorData.items():
            input(f'put the rover on {color}')
            self.colorData[color] = self.get_color()

        with open("resources/colorData.json", "w") as data:
            json.dump(self.colorData, data)

        print("calibration completed")
