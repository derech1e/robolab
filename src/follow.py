import time
import math
from typing import Tuple, List

from sensors.color_sensor import *
from sensors.motor_sensor import *
from sensors.touch_sensor import *
from sensors.sonar_sensor import SonarSensor
from enums import StopReason
from planet import Direction

from odometry import Odometry


class Follow:
    def __init__(self, color_sensor: ColorSensor, motor_sensor: MotorSensor) -> None:
        self.sonar_sensor = SonarSensor()
        self.color_sensor = color_sensor
        self.colorData = self.color_sensor.return_color()
        self.motor_sensor = motor_sensor
        self.avrLightness = (self.colorData["white"][1] + self.colorData["black"][1]) / 2
        self.integral_value = 0
        self.timer = 0
        self.last_error = 0

        self.odo = Odometry()

        # TODO: tune these values
        self.normalSpeed = 150
        self.TURN_SPEED = 150
        self.AXLE_LENGTH = 10
        self.KA = 1  # to skale all
        self.KP = 0.51  # Aktueller Fehler ??
        self.KI = 0.074  # Bisherige Fehler ??
        self.KD = 0.45  # Zukünftige Fehler ??
        self.INTEGRAL_FACTOR = 0.587  # In kurven??

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
        return self.normalSpeed + int(self.calc_turn())

    def calc_speed_right(self) -> int:
        return self.normalSpeed - int(self.calc_turn())

    def turn_until_line_detected(self):
        self.line_detection_in_progress = True
        print("Turning until line")
        self.motor_sensor.turn_angle_blocking(200, 350)
        print("Bayblade")
        self.motor_sensor.beyblade(100)
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
        # angle = int(round(angle + 360)) % 360

        """if 0 <= angle < 35:
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
            return 0"""

        return Direction((round(angle / 90) * 90 + 360) % 360)

    def scan_node(self) -> [Direction]:

        # fahre bis keine farbe mehr
        # dreh dich und behalte den winkel im blich
        # wenn du in einen neuene quadranten kommst, schecke nach schwarz
        # note = {pos, }

        while self.color_sensor.get_hls_color_name() in ["red", "blue"]:
            self.motor_sensor.forward_non_blocking(self.normalSpeed, self.normalSpeed)
        # evtl sleep hier um weiter zu fahren
        self.motor_sensor.forward_relative_blocking(40, self.normalSpeed)
        self.motor_sensor.stop()

        alpha = 0
        directions: [Direction] = []
        old_pos = (self.motor_sensor.beyblade(0))

        # for angle in [math.pi / 2 - 0.1, math.pi - 0.1, math.pi * 3 / 2 - 0.1, math.pi *2 -0.1]:
        for i in range(1, 5):
            angle = math.pi * i / 2
            while alpha < angle + 1:
                new_pos = self.motor_sensor.beyblade(self.TURN_SPEED)
                delta_pos = (new_pos[0] - old_pos[0], new_pos[1] - old_pos[1])
                old_pos = new_pos
                alpha = alpha + (delta_pos[1] - delta_pos[0]) / self.AXLE_LENGTH * 0.05

                if (self.color_sensor.get_color_hls()[1] < 100
                        and alpha > angle - 0.5
                        and self.color_sensor.get_hls_color_name() == "black"):
                    directions.append(self.angle_to_direction(360 - 90 * i))
                    print("path detected")
                    break

        print(f"scan_node: {directions}")
        self.motor_sensor.stop()
        self.node_scan_done = False
        print("scan_node: done!")

        print("Correct base heading")
        self.motor_sensor.turn_angle_blocking(-70, 50)

        return directions

    def follow(self) -> StopReason:
        while True:
            if self.color_sensor.is_node():
                self.motor_sensor.stop()
                self.odo.update_position(self.motor_sensor.motor_positions)
                self.odo.get_coordinates()
                return StopReason.NODE  # Stop following if node is detected
            if self.sonar_sensor.is_colliding():
                return StopReason.COLLISION  # Stop following collision is detected

            self.motor_sensor.forward_non_blocking(self.calc_speed_left(), self.calc_speed_right())



