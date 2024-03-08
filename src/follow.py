from sensors.color_sensor import *
from sensors.motor_sensor import *


class Follow:
    def __init__(self) -> None:
        self.motor_sensor = Driver()
        self.color_sensor = ColorSensor()
        self.colorData = self.color_sensor.returnColor()
        # self.avrColor = (self.colorData["white"][0] + self.colorData["white"][1] + self.colorData["white"][2] \
        #                 + self.colorData["black"][0] + self.colorData["black"][1] + self.colorData["black"][2]) // 2
        self.avrLightness = self.colorData["white"][2] + self.colorData["black"][2]
 
        # TODO: tune these values
        self.Kp = 10
        self.normalSpeed = 100


    def calcError(self) -> int:
        color = self.color_sensor.getColorHLS()
        error = self.avrLightness - color[2]
        return error  

    def calcTurn(self) -> int:
        return self.Kp * self.calcError()

    def calcSpeedLeft(self) -> int:
        return self.normalSpeed - self.calcTurn()

    def calcSpeedRight(self) -> int:
        return self.normalSpeed + self.calcTurn()

    def follow(self):
        self.motor_sensor.drive(self.normalSpeed, self.normalSpeed)
        while not self.color_sensor.checkColor():
            self.motor_sensor.drive(self.calcSpeedLeft, self.calcSpeedLeft)

