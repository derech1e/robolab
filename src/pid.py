from typing import Tuple
from sensors.color_sensor import ColorSensor
from sensors.motor_sensor import MotorSensor
import Constants


class PID:
    def __init__(self, color_sensor: ColorSensor, motor_sensor: MotorSensor):
        self.color_sensor = color_sensor
        self.motor_sensor = motor_sensor

        self.integral_value = 0
        self.last_error = 0

    def calc_error(self) -> tuple[float, float]:
        error = self.color_sensor.get_brightness_error()
        self.integral_value = Constants.INTEGRAL_FACTOR * self.integral_value + error
        delta_error = error - self.last_error
        self.last_error = error
        return error, delta_error

    def calc_turn(self) -> float:
        error, delta_error = self.calc_error()
        return round(Constants.KP * error + Constants.KI * self.integral_value + Constants.KD * delta_error)

    def calc_speed(self) -> Tuple[int, int]:
        return Constants.SPEED + self.calc_turn(), Constants.SPEED - self.calc_turn()

    def stop(self):
        self.motor_sensor.stop()
