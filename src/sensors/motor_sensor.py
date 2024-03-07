import time

import ev3dev.ev3 as ev3


class MotorSensor:
    def __init__(self):
        self.motor_left = ev3.LargeMotor("outA")
        self.motor_left.reset()
        self.i = 0
        # self.motor_left.stop_action = "brake"

        self.motor_right = ev3.LargeMotor("outD")
        self.motor_right.reset()
        # self.motor_right.stop_action = "brake"

    def turn(self, deg):
        self.__update_speed(self.motor_left, deg)
        self.__update_speed(self.motor_right, -deg)
        while self.motor_left.position < 140 or self.motor_right.position > -140:
            print(f"Left: {self.motor_left.position}, Right: {self.motor_right.position}")
            time.sleep(0.005)
            self.i += 1
        self.stop()

    def turn_180(self):
        pass

    def __update_speed(self, motor: ev3.LargeMotor, speed):
        motor.speed_sp = speed
        motor.command = "run-forever"

    # input from -100 to 100
    def forward(self, speed):
        self.__update_speed(self.motor_left, speed)
        self.__update_speed(self.motor_right, speed)

    def stop(self):
        self.motor_left.stop()
        self.motor_right.stop()
