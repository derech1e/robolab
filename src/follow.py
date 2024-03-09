import time
import csv

from sensors.color_sensor import *
from sensors.motor_sensor import *
from sensors.speaker_sensor import SpeakerSensor
from sensors.touch_sensor import *


class Follow:
    def __init__(self) -> None:
        self.motor_sensor = MotorSensor()
        self.color_sensor = ColorSensor()
        self.speaker_sensor = SpeakerSensor()
        self.colorData = self.color_sensor.return_color()
        # self.avrColor = (self.colorData["white"][0] + self.colorData["white"][1] + self.colorData["white"][2] \
        #                 + self.colorData["black"][0] + self.colorData["black"][1] + self.colorData["black"][2]) // 2
        self.avrLightness = (self.colorData["white"][1] + self.colorData["black"][1]) / 2
        self.integral_value = 0
        self.timer = 0
        self.last_error = 0

        # TODO: tune these values
        self.normalSpeed = 150
        self.KA = 1  # to skale all
        self.KP = 0.51
        self.KI = 0.074
        self.KD = 0.45
        self.INTEGRAL_FACTOR = 0.587

        # test
        self.state = False
        self.sensorT = TouchSensor()
        self.dataPlot = []

    # 350 = WHITE
    # 50 = BLACK

    def calc_error(self) -> tuple[float, float]:
        color = self.color_sensor.get_color_hls()
        error = self.avrLightness - color[1]

        # update integral (erhoet sich um 70)
        self.integral_value = self.INTEGRAL_FACTOR * self.integral_value + error
        delta_error = error - self.last_error
        self.last_error = error
        return error, delta_error

    def calc_turn(self) -> float:
        error, delta_error = self.calc_error()
        return self.KA * (self.KP * error + self.KI * self.integral_value + self.KD * delta_error)

    def calc_speed_left(self) -> int:
        # print(f"Calc turn: {self.calc_turn()}")
        return self.normalSpeed + int(self.calc_turn())

    def calc_speed_right(self) -> int:
        return self.normalSpeed - int(self.calc_turn())

    def follow(self):
        if self.color_sensor.get_hls_color_name() == "red" or self.color_sensor.get_hls_color_name() == "blue":
            self.motor_sensor.stop()
            print("Motor stopped")
        else:
            self.motor_sensor.forward(self.calc_speed_left(), self.calc_speed_right())
