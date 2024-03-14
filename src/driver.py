# imports
import math
import time

from enums import StopReason
from planet import Direction
from sensors.color_sensor import ColorSensor
from sensors.sonar_sensor import SonarSensor
from sensors.motor_sensor import MotorSensor
from pid import PID
import constants


class Driver:
    def __init__(self, motor_sensor: MotorSensor, color_sensor: ColorSensor):
        self.color_sensor = color_sensor
        self.motor_sensor = motor_sensor
        self.sonar_sensor = SonarSensor()
        self.pid = PID(color_sensor, motor_sensor)

        self.is_first_node = True

    def turn_find_line(self):
        while self.color_sensor.get_luminance() > self.color_sensor.AVR_LIGHTNESS:
            self.motor_sensor.drive_with_speed(-100, 100)
        self.motor_sensor.stop()
        print("Line found")

        # TODO: if the robot is not on the line, add code for slower turning in opposite direction

    def follow_line(self) -> StopReason:
        self.motor_sensor.reset_position()
        stop_reason = StopReason.NODE

        while True:
            speed = self.pid.calc_speed()
            self.motor_sensor.drive_with_speed(speed[0], speed[1])

            # check for collision
            if self.sonar_sensor.is_colliding():
                print("Collision detected")
                self.motor_sensor.stop()

                # turn and find line
                self.motor_sensor.turn_angle(90)
                self.turn_find_line()
                stop_reason = StopReason.COLLISION

            if self.color_sensor.is_node():
                print("Node detected")
                if self.is_first_node:
                    stop_reason = StopReason.FIRST_NODE
                    self.is_first_node = False

                self.motor_sensor.stop()
                break

        return stop_reason

    def rotate_to_line(self, direction: Direction):
        self.motor_sensor.turn_angle(direction.value)
        self.turn_find_line()

    def scan_node(self, incoming_direction: Direction) -> list[Direction]:
        while self.color_sensor.get_color_name() in ["red", "blue"]:
            self.motor_sensor.drive_with_speed(constants.SPEED, constants.SPEED)

        self.motor_sensor.drive_cm(2, constants.SPEED)

        alpha = 0
        angle = 0
        directions: [Direction] = []
        old_pos = (self.motor_sensor.beyblade(0))

        # for angle in [math.pi / 2 - 0.1, math.pi - 0.1, math.pi * 3 / 2 - 0.1, math.pi *2 -0.1]:
        # for i in range(1, 5):
        #     angle = math.pi * i / 2
        #     while alpha < angle + 0.3:  # TODO: Scale this value with battery voltage level (0.3 - 1.0)
        #         new_pos = self.motor_sensor.beyblade(150)
        #         delta_pos = (new_pos[0] - old_pos[0], new_pos[1] - old_pos[1])
        #         old_pos = new_pos
        #         alpha = alpha + (delta_pos[1] - delta_pos[0]) / constants.AXLE_LENGTH * 0.05
        #         print(self.color_sensor.get_color_name())
        #         if (self.color_sensor.get_color_hls()[1] < 100
        #                 and alpha > angle - 0.5
        #                 and self.color_sensor.get_color_name() == "black"):
        #             directions.append(Direction(360 - 90 * i))
        #             print("path detected")
        #             break
        for i in [0, 1, 3, 4]:
            angle = math.pi * i / 2
            while alpha < angle + (0 if i == 4 else 0.3):
                angle = math.pi * i / 2
                new_pos = self.motor_sensor.beyblade(150)
                delta_pos = (new_pos[0] - old_pos[0], new_pos[1] - old_pos[1])
                old_pos = new_pos
                alpha = alpha + (delta_pos[1] - delta_pos[0]) / constants.AXLE_LENGTH * 0.05
                if (self.color_sensor.get_color_hls()[1] < 100
                        and alpha > angle - 0.3
                        and self.color_sensor.get_color_name() == "black"):
                    dir = ((incoming_direction.value + 360 - 90 * i) % 360)
                    print(dir)
                    directions.append(Direction(dir))
                    print("path detected")
                    break

        self.motor_sensor.stop()
        print(f"angle to go to: {angle}, real angle: {alpha}")
        print(f"scan_node: {directions}")
        print("scan_node: done!")

        print("Correct base heading")
        # self.motor_sensor.turn_angle_blocking(-80, 50)

        return directions
