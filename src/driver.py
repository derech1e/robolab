# imports
import time

from enums import StopReason
from planet import Direction
from sensors.color_sensor import ColorSensor
from sensors.sonar_sensor import SonarSensor
from sensors.motor_sensor import MotorSensor
from sensors.speaker_sensor import *
from pid import PID
import constants


class Driver:
    def __init__(self, motor_sensor: MotorSensor, color_sensor: ColorSensor, speaker_sensor: SpeakerSensor):
        self.color_sensor = color_sensor
        self.motor_sensor = motor_sensor
        self.sonar_sensor = SonarSensor()
        self.speaker_sensor = speaker_sensor
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
                self.speaker_sensor.play_tone()

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

        # self.motor_sensor.reset_position()
        self.motor_sensor.stop()
        return stop_reason

    def rotate_to_line(self, direction: float):  # direction: Direction
        # turn less than full and find line only if more than 20 deg rotation
        if direction > 0:
            self.motor_sensor.turn_angle(direction - 20)
            self.turn_find_line()
        else:
            self.turn_find_line()

    @staticmethod
    def angle_to_direction(angle):
        if 0 <= angle <= 160:
            return 0
        elif 160 <= angle <= 290:
            return 270
        elif 290 <= angle <= 420:
            return 180
        elif 420 <= angle < 550:
            return 90

        return 0  # Default

    def scan_node(self) -> list[Direction]:
        # incoming_direction = Direction((180 + incoming_direction.value) % 360)
        self.motor_sensor.stop()
        print("scanning node...")
        while self.color_sensor.get_color_name():
            self.motor_sensor.drive_with_speed(constants.SPEED, constants.SPEED)
        print(self.color_sensor.get_color_name())

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
                print(f"pos: {position}")
                direction = Direction(self.angle_to_direction(position))
                # direction = Direction((self.angle_to_direction(position) + incoming_direction.value) % 360)
                if direction not in directions:
                    directions.append(direction)
                    print("Detected node", direction)

        south = Direction.SOUTH
        if south in directions:
            directions.remove(south)
        self.motor_sensor.stop()
        return directions
