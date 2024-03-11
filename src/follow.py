import time
import csv
from typing import Tuple

from sensors.color_sensor import *
from sensors.motor_sensor import *
from sensors.touch_sensor import *
from sensors.sonar_sensor import SonarSensor
from planet import Direction


class Follow:
    def __init__(self, color_sensor: ColorSensor) -> None:
        self.motor_sensor = MotorSensor()
        self.sonar_sensor = SonarSensor()
        self.color_sensor = color_sensor
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
        self.line_detection_in_progress = False

        # Node scan
        self.node_scan_done = False  # REMOVE THIS BULLSHIT LATER AND REPLACE IT WITH AN ARRAY OF THE COORDS

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
        self.line_detection_in_progress = True
        self.motor_sensor.turn_angle_blocking(200, 350)
        self.motor_sensor.beyblade(-100)
        while True:
            color = self.color_sensor.get_hls_color_name()
            time.sleep(0.1)
            if color == "black":
                self.motor_sensor.stop()
                self.line_detection_in_progress = False
                print("Black line detected")
                break

    def stop(self):
        self.motor_sensor.stop()

    def angle_to_direction(self, angle):
        angle = int(round(angle + 360)) % 360
        if 0 <= angle < 35:
            return 0
        elif 50 < angle < 120:
            return Direction.WEST  # 90
        elif 140 < angle < 210:
            return Direction.SOUTH  # 180
        elif 230 < angle < 300:
            return Direction.EAST  # 270
        elif 325 < angle < 360:
            return 0
        else:
            return 0

    def scan_node(self):
        self.motor_sensor.stop()
        self.motor_sensor.forward_relative_blocking(100, 100)
        self.motor_sensor.beyblade(50)
        scanned_nodes = []

        while True:
            position = self.motor_sensor.get_position()
            angle = self.motor_sensor.position_to_angle(position)
            color = self.color_sensor.get_hls_color_name()
            print(f"Position: {position}, Angle: {angle}, Color: {color}")
            time.sleep(0.1)
            if color == "black":
                direction = self.angle_to_direction(angle)
                if direction not in scanned_nodes:
                    scanned_nodes.append(self.angle_to_direction(angle))
                    print("Detected node")
            if angle > 380:
                self.motor_sensor.stop()
                print("EXIT")
                break

        self.motor_sensor.forward_relative_blocking(-500, 100)

    def follow(self):
        # print(self.color_sensor.get_color_hls())
        # time.sleep(5)
        if (self.color_sensor.get_hls_color_name() == "red" or self.color_sensor.get_hls_color_name() == "blue") and not self.node_scan_done:
            self.motor_sensor.stop()
            print("Color detected!")
            time.sleep(3)
            self.node_scan_done = True
            self.scan_node()
        else:
            self.motor_sensor.forward_non_blocking(self.calc_speed_left(), self.calc_speed_right())
