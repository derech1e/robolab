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

    # 155 = 90°
    # 310 = 180°
    # 620 = 370°
    # 610 = 360°
    # 1220 = 730
    # 1210 = 720

    def save_motor_positions(self):
        self.motor_positions.append((self.motor_left.position, self.motor_right.position))

    def get_motor_positions(self) -> list[tuple[int, int]]:
        return self.motor_positions


    def turn(self, deg, clockwise=True):

        self.__update_speed(self.motor_left, 50 if clockwise else -50)
        self.__update_speed(self.motor_right, -50 if clockwise else 50)
        offset = deg * self.ROTATION_PER_DEGREE
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
