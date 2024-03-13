# imports
from enums import StopReason
from planet import Direction
from sensors.color_sensor import ColorSensor
from sensors.sonar_sensor import SonarSensor
from sensors.motor_sensor import MotorSensor
from pid import PID


class Driver:
    def __init__(self, motor_sensor: MotorSensor, color_sensor: ColorSensor):
        self.color_sensor = color_sensor
        self.motor_sensor = motor_sensor
        self.sonar_sensor = SonarSensor()
        self.pid = PID(color_sensor, motor_sensor)

        self.is_first_node = False

    def turn_find_line(self):
        while self.color_sensor.get_luminance() < self.color_sensor.AVR_LIGHTNESS:
            self.motor_sensor.drive_with_speed(-50, 50)

        # TODO: if the robot is not on the line, add code for slower turning in opposite direction

    def follow_line(self) -> StopReason:
        self.motor_sensor.reset_position()
        stop_reason = StopReason.NODE

        while True:
            speed = self.pid.calc_speed()
            self.motor_sensor.drive_with_speed(speed[0], speed[1])

            # check for collision
            if self.sonar_sensor.is_colliding():
                self.motor_sensor.stop()

                # turn and find line
                self.motor_sensor.turn_angle(90)
                self.turn_find_line()
                stop_reason = StopReason.COLLISION

            if self.color_sensor.is_node():
                if self.is_first_node:
                    stop_reason = StopReason.FIRST_NODE
                    self.is_first_node = False

                self.motor_sensor.stop()
                break

        return stop_reason

    def rotate_to_line(self, direction: Direction):
        self.motor_sensor.turn_angle(direction.value)
        self.turn_find_line()
