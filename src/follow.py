import time
import csv

from sensors.color_sensor import *
from sensors.motor_sensor import *
from sensors.speaker_sensor import SpeakerSensor
from sensors.touch_sensor import *
from sensors.sonar_sensor import SonarSensor


class Follow:
    def __init__(self) -> None:
        self.motor_sensor = MotorSensor()
        self.sonar_sensor = SonarSensor()
        self.color_sensor = ColorSensor()
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
        self.KP = 0.51  # Aktueller Fehler ??
        self.KI = 0.074  # Bisherige Fehler ??
        self.KD = 0.45  # Zukünftige Fehler ??
        self.INTEGRAL_FACTOR = 0.587  # In kurven??

        # test
        self.state = False
        self.sensorT = TouchSensor()
        self.dataPlot = []

        # Collision detection
        self.collision_turn_in_progress = False

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
        return self.KP * error + self.KI * self.integral_value + self.KD * delta_error

    def calc_speed_left(self) -> int:
        # print(f"Calc turn: {self.calc_turn()}")
        return self.normalSpeed + int(self.calc_turn())

    def calc_speed_right(self) -> int:
        return self.normalSpeed - int(self.calc_turn())

    def turn_until_line_detected(self):
        self.collision_turn_in_progress = True
        self.motor_sensor.turn_relative_angle(150, 200)
        self.motor_sensor.beyblade(-100)
        while True:
            color = self.color_sensor.get_hls_color_name()
            time.sleep(0.1)
            if color == "black":
                self.motor_sensor.stop()
                self.collision_turn_in_progress = False
                print("Black line detected")
                break

    def stop(self):
        self.motor_sensor.stop()

    def follow(self):
        # print(self.color_sensor.get_color_hls())
        # time.sleep(5)
        if self.color_sensor.get_hls_color_name() == "red" or self.color_sensor.get_hls_color_name() == "blue":
            self.motor_sensor.stop()
            print("Motor stopped")
            time.sleep(3)
        else:
            self.motor_sensor.forward(self.calc_speed_left(), self.calc_speed_right())
