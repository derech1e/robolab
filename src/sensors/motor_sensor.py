import time

import ev3dev.ev3 as ev3


class MotorSensor:
    def __init__(self):
        self.motor_left = ev3.LargeMotor("outA")
        self.motor_left.reset()
        self.motor_left.stop_action = "brake"

        self.motor_right = ev3.LargeMotor("outD")
        self.motor_right.reset()
        self.motor_right.stop_action = "brake"

        self.ROTATION_PER_DEGREE = 1.694392166

        self.motor_positions = [(self.motor_left.position, self.motor_right.position)]

    def save_motor_positions(self):
        self.motor_positions.append((self.motor_left.position, self.motor_right.position))

    def get_motor_positions(self) -> list[tuple]:
        return self.motor_positions

    # Battery level: cat /sys/devices/platform/battery/power_supply/lego-ev3-battery/voltage_now

    def __angle_multiplier(self, angle):
        angle = angle % 360
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

    def __update_relative(self, motor, position, speed):
        motor.position_sp = position
        motor.speed_sp = speed
        motor.command = "run-to-rel-pos"

    def turn_relative_angle(self, angle):
        offset = angle * self.__angle_multiplier(angle)

        self.__update_relative(self.motor_left, offset, 50)
        self.__update_relative(self.motor_right, -offset, 50)

        self.motor_left.wait_until_not_moving()
        self.motor_right.wait_until_not_moving()

    def turn(self, deg):
        self.__update_speed(self.motor_left, 50)
        self.__update_speed(self.motor_right, -50)
        offset = deg * self.__angle_multiplier(deg)
        while True:
            # TODO: Impl reverse pre sign on the line below for counter clockwise rotation
            if not (self.motor_left.position < offset or self.motor_right.position > -offset):
                self.stop()
                break
            # print(f"Left: {self.motor_left.position}, Right: {self.motor_right.position}")
            # time.sleep(0.1)
        # self.stop()

    def turn_180(self):
        pass

    def __update_speed(self, motor: ev3.LargeMotor, speed):
        motor.speed_sp = speed
        motor.command = "run-forever"

    # input from -100 to 100
    def forward(self, speed_left: int, speed_right: int):
        self.__update_speed(self.motor_left, speed_left)
        self.__update_speed(self.motor_right, speed_right)
        self.motor_positions.append((self.motor_left.position, self.motor_right.position))

    def stop(self):
        self.motor_left.stop()
        self.motor_right.stop()
        self.motor_right.reset()
        self.motor_right.stop_action = "brake"
        self.motor_left.reset()
        self.motor_left.stop_action = "brake"

        # TODO: Might impl. reset function
