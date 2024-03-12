import time

import ev3dev.ev3 as ev3


class MotorSensor:
    def __init__(self):
        self.motor_left = ev3.LargeMotor("outA")
        self.motor_left.reset()
        self.motor_left.stop_action = "hold"

        self.motor_right = ev3.LargeMotor("outD")
        self.motor_right.reset()
        self.motor_right.stop_action = "hold"

        self.ROTATION_PER_DEGREE = 1.694392166

        self.motor_positions = [(self.motor_left.position, self.motor_right.position)]

    def save_motor_positions(self):
        self.motor_positions.append((self.motor_left.position, self.motor_right.position))

    def get_motor_positions(self) -> list[tuple[int, int]]:
        return self.motor_positions

    # Battery level: cat /sys/devices/platform/battery/power_supply/lego-ev3-battery/voltage_now

    def __angle_multiplier(self, angle):
        angle = int(round(angle + 360)) % 360
        print(angle)
        # 155 = 90° => 1.722222
        # 150 = 90° ONLY on full charge  => 1.66667
        # 300 = 180° ONLY on full charge
        # 310 = 180°
        # 610 = 360°
        # 620 = 370°
        # 1210 = 720°
        # 1220 = 730°
        if angle <= 90:
            return 1.64667
        elif 90 < angle <= 180:
            return 1.6677
        elif angle <= 270:
            return 1.65
        else:
            return 1.62

    def position_to_angle(self, position):
        return position / 1.694

    def turn_angle_blocking(self, angle, speed=50):
        offset = angle * self.__angle_multiplier(angle)

        self.__update_speed_position_relative(self.motor_left, -offset, speed)
        self.__update_speed_position_relative(self.motor_right, offset, speed)

        self.motor_left.wait_until_not_moving()
        self.motor_right.wait_until_not_moving()

    def turn_angle_non_blocking(self, deg):
        self.__update_speed(self.motor_left, 50)
        self.__update_speed(self.motor_right, -50)
        offset = deg * self.__angle_multiplier(deg)
        while True:
            if not (self.motor_left.position < offset or self.motor_right.position > -offset):
                self.stop()
                break

    def beyblade(self, speed):
        self.__update_speed(self.motor_left, -speed)
        self.__update_speed(self.motor_right, speed)
        return self.motor_left.position, self.motor_right.position

    def get_position(self):
        return (abs(self.motor_left.position) + abs(self.motor_right.position)) / 2

    def __update_speed(self, motor: ev3.LargeMotor, speed):
        motor.speed_sp = speed
        motor.command = "run-forever"

    def __update_speed_position_relative(self, motor, position, speed):
        motor.position_sp = position
        motor.speed_sp = speed
        motor.command = "run-to-rel-pos"

    # input from -100 to 100
    def forward_non_blocking(self, speed_left: int, speed_right: int):
        self.__update_speed(self.motor_left, speed_left)
        self.__update_speed(self.motor_right, speed_right)
        self.motor_positions.append((self.motor_left.position, self.motor_right.position))

    def forward_relative_blocking(self, position, speed):
        self.__update_speed_position_relative(self.motor_left, position, speed)
        self.__update_speed_position_relative(self.motor_right, position, speed)

        self.motor_left.wait_until_not_moving()
        self.motor_right.wait_until_not_moving()

    def is_running(self):
        return self.motor_right.is_running or self.motor_left.is_running

    def stop(self):
        self.motor_left.stop()
        self.motor_right.stop()
        # self.motor_right.reset()
        self.motor_right.stop_action = "hold"
        # self.motor_left.reset()
        self.motor_left.stop_action = "hold"
