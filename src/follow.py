from sensors.color_sensor import *
from sensors.motor_sensor import *


class Follow:
    def __init__(self) -> None:
        self.motor_sensor = Driver()
        self.color_sensor = ColorSensor()
        self.colorData = self.color_sensor.return_color()
        # self.avrColor = (self.colorData["white"][0] + self.colorData["white"][1] + self.colorData["white"][2] \
        #                 + self.colorData["black"][0] + self.colorData["black"][1] + self.colorData["black"][2]) // 2
        self.avrLightness = self.colorData["white"][2] + self.colorData["black"][2]
 
        # TODO: tune these values
        self.Kp = 10
        self.normalSpeed = 100


    def calc_error(self) -> float:
        color = self.color_sensor.get_color_HLS()
        error = self.avrLightness - color[2]
        return error  

    def calc_turn(self) -> float:
        return self.Kp * self.calc_error()

    def calc_speed_left(self) -> int:
        return self.normalSpeed - int(self.calc_turn())

    def calc_speed_right(self) -> int:
        return self.normalSpeed + int(self.calc_turn())

    def follow(self):
        self.motor_sensor.drive(self.normalSpeed, self.normalSpeed)
        while not self.color_sensor.check_color_HLS():
            self.motor_sensor.drive(self.calc_speed_left, self.calc_speed_left)

