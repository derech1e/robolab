import time
import csv

from sensors.color_sensor import *
from sensors.motor_sensor import *
from sensors.speaker_sensor import SpeakerSensor
from sensors.touch_sensor import *

from odometry import Odometry


class Follow:
    def __init__(self) -> None:
        self.motor_sensor = MotorSensor()
        self.color_sensor = ColorSensor()
        self.speaker_sensor = SpeakerSensor()
        self.colorData = self.color_sensor.return_color()
        # self.avrColor = (self.colorData["white"][0] + self.colorData["white"][1] + self.colorData["white"][2] \
        #                 + self.colorData["black"][0] + self.colorData["black"][1] + self.colorData["black"][2]) // 2
        self.avrLightness = (self.colorData["white"][1] + self.colorData["black"][1]) / 2
        self.integral_value = 0
        self.timer = 0
        self.last_error = 0

        # TODO: tune these values
        self.normalSpeed = 200
        self.KA = 1 # to skale all
        self.KP = 0.75
        self.KI = 0
        self.KD = 0
        self.KEEP_INTEGRAL = 1

        #test
        self.state = False
        self.sensorT = TouchSensor()
        self.dataPlot = []
        self.odo = Odometry()

    # 350 = WHITE
    # 50 = BLACK

    def calc_error(self) -> tuple[float,float]:
        color = self.color_sensor.get_color_hls()
        error = self.avrLightness - color[1]

        #update integral (erhoet sich um 70)
        self.integral_value = self.KEEP_INTEGRAL * self.integral_value + error
        delta_error = error - self.last_error
        self.last_error = error
        return error, delta_error


    def calc_turn(self) -> float:
        error, delta_error = self.calc_error()
        # print(f"error: {error}, p-part: {error*self.KP}, i-part: {self.KI * self.integral_value}, d-part: {self.KD * delta_error}")
        # self.dataPlot.append(f"{time.time()},{error*self.KP},{self.KI * self.integral_value},{delta_error}")
        self.dataPlot.append((time.time(), error*self.KP, self.KI * self.integral_value, self.KD * delta_error, self.KP * error + self.KI * self.integral_value + self.KP * delta_error))
        return self.KA * (self.KP * error + self.KI * self.integral_value + self.KP * delta_error)

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
                # print(self.motor_sensor.get_motor_positions())
                self.odo.update_position(self.motor_sensor.get_motor_positions())
                
                break
                # time.sleep(2)
                # self.motor_sensor.forward(self.calc_speed_left(), self.calc_speed_right())

            self.motor_sensor.forward(self.calc_speed_left(), self.calc_speed_right())

            # while self.sensorT.is_pressed():
            #     self.state = True
            #     pass
            # if self.state:
            #     self.KP += 0.05
            #     self.dataPlot = []
            #     print(f"KI: {self.KI}")
            #     self.state = False

        #writing data to csv
            # if self.sensorT.is_pressed():
            #     break

        print("writing")
        with open('sensors/data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["t", f"KP={self.KP}", f"KI={self.KI}", f"KD={self.KD}","turn"])
            writer.writerows(self.dataPlot)
        print("finished writing")


            

            
