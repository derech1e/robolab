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
                self.motor_sensor.turn_angle(30)
                self.turn_find_line()
                stop_reason = StopReason.COLLISION

            if self.color_sensor.is_node():
                print("Node detected")
                if self.is_first_node:
                    stop_reason = StopReason.FIRST_NODE
                    self.is_first_node = False
                break

        self.motor_sensor.reset_position()
        return stop_reason

    def rotate_to_line(self, direction: Direction):
        self.motor_sensor.turn_angle(direction.value)
        self.turn_find_line()

    def angle_to_direction(self, angle):
        # angle = int(round(angle + 360)) % 360
        if 0 <= angle <= 180:
            return 0
        elif 180 <= angle <= 340:
            return 270  # 90
        elif 340 <= angle <= 520:
            return 180  # 180
        elif 520 <= angle < 700:
            return 90  # 270

        return 0  # Default

    def scan_node(self) -> list[Direction]:
        # incoming_direction = Direction((180 + incoming_direction.value) % 360)
        self.motor_sensor.stop()
        print("scanning node...")
        while self.color_sensor.get_color_name():
            self.motor_sensor.drive_with_speed(constants.SPEED, constants.SPEED)

        self.motor_sensor.drive_cm(1.5, 1.5, constants.SPEED)
        self.motor_sensor.turn_angle(-30)

        self.motor_sensor.reset_position()

        time.sleep(0.3)

        directions = []

        self.motor_sensor.full_turn()

        while self.motor_sensor.is_running():
            position = self.motor_sensor.get_position()
            luminance = self.color_sensor.get_luminance()
            # print(position)
            time.sleep(0.1)
            # print(luminance)
            if luminance < 85:
                print("DETECTED")
                direction = Direction(self.angle_to_direction(position))
                # direction = Direction((self.angle_to_direction(position) + incoming_direction.value) % 360)
                if direction not in directions:
                    directions.append(direction)
                    # print("Detected node", direction)

        south = Direction.SOUTH
        if south in directions:
            directions.remove(south)
        self.motor_sensor.stop()
        return directions
