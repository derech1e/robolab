import time

from sensors.color_sensor import *
from sensors.motor_sensor import *
from sensors.speaker_sensor import SpeakerSensor


class Follow:
    def __init__(self) -> None:
        self.motor_sensor = MotorSensor()
        self.color_sensor = ColorSensor()
        self.speaker_sensor = SpeakerSensor()
        self.colorData = self.color_sensor.return_color()
        # self.avrColor = (self.colorData["white"][0] + self.colorData["white"][1] + self.colorData["white"][2] \
        #                 + self.colorData["black"][0] + self.colorData["black"][1] + self.colorData["black"][2]) // 2
        self.avrLightness = (self.colorData["white"][1] + self.colorData["black"][1]) / 2

        # TODO: tune these values
        self.normalSpeed = 250
        self.Kp = 1

    # 350 = WHITE
    # 50 = BLACK

    def calc_error(self) -> float:
        color = self.color_sensor.get_color_hls()
        error = self.avrLightness - color[1]
        # print(f"Error: {error}, AVG: {self.avrLightness}, HLS: {color[1]}")
        return error

    def calc_turn(self) -> float:
        return self.Kp * self.calc_error()

    def calc_speed_left(self) -> int:
        # print(f"Calc turn: {self.calc_turn()}")
        return self.normalSpeed + int(self.calc_turn())

    def calc_speed_right(self) -> int:
        return self.normalSpeed - int(self.calc_turn())

    def follow(self):
        # print("Init driving forward")
        # self.motor_sensor.drive(self.normalSpeed, self.normalSpeed)
        # print("Driving forward")

        while True:
            if self.color_sensor.get_hls_color_name() == "red" or self.color_sensor.get_hls_color_name() == "blue":
                self.motor_sensor.stop()
                self.speaker_sensor.play_beep()
                time.sleep(2)
                self.motor_sensor.forward(self.calc_speed_left(), self.calc_speed_right())

            self.motor_sensor.forward(self.calc_speed_left(), self.calc_speed_right())
