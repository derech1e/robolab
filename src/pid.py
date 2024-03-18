from typing import Tuple
from sensors.color_sensor import ColorSensor
from sensors.motor_sensor import MotorSensor
import constants


class PID:
    """
    This class is responsible for P I D controlling of the robot
    """
    def __init__(self, color_sensor: ColorSensor, motor_sensor: MotorSensor):
        """
        Initializes the PID
        """
        self.color_sensor = color_sensor
        self.motor_sensor = motor_sensor

        self.integral_value = 0
        self.last_error = 0

    def __get_brightness_error(self) -> float:
        """
        Returns the brightness error of the current following path
        :return: float
        """
        return self.color_sensor.average_lightness - self.color_sensor.get_luminance()

    def calc_error(self) -> tuple[float, float]:
        """
        Calculates integral value and delta error from brightness error
        :return: tuple[float, float]
        """
        error = self.__get_brightness_error()
        self.integral_value = constants.INTEGRAL_FACTOR * self.integral_value + error
        delta_error = error - self.last_error
        self.last_error = error
        return error, delta_error

    def calc_turn(self) -> float:
        """
        Calculates turn value from current error values
        :return: float
        """
        error, delta_error = self.calc_error()
        return round(constants.KP * error + constants.KI * self.integral_value + constants.KD * delta_error)

    def calc_speed(self) -> Tuple[int, int]:
        """
        Calculates speed for left and right motors based on calculated turn value
        :return: Tuple[int, int]
        """
        return constants.SPEED + self.calc_turn(), constants.SPEED - self.calc_turn()

    def stop(self) -> None:
        """
        Stops the motor
        :return: Void
        """
        self.motor_sensor.stop()
