from sensors.color_sensor import *
from sensors.motor_sensor import *
from planet import Direction

import constants


class Follow:
    def __init__(self, color_sensor: ColorSensor, motor_sensor: MotorSensor) -> None:
        self.color_sensor = color_sensor
        self.motor_sensor = motor_sensor

    def scan_node(self) -> list[Direction]:

        # fahre bis keine farbe mehr
        # dreh dich und behalte den winkel im blich
        # wenn du in einen neuene quadranten kommst, schecke nach schwarz
        # note = {pos, }

        while self.color_sensor.get_color_name() in ["red", "blue"]:
            self.motor_sensor.forward_non_blocking(constants.SPEED, constants.SPEED)
        # evtl sleep hier um weiter zu fahren
        self.motor_sensor.forward_relative_blocking(40, constants.SPEED)
        self.motor_sensor.stop()

        alpha = 0
        directions: [Direction] = []
        old_pos = (self.motor_sensor.beyblade(0))

        # for angle in [math.pi / 2 - 0.1, math.pi - 0.1, math.pi * 3 / 2 - 0.1, math.pi *2 -0.1]:
        for i in range(1, 5):
            angle = math.pi * i / 2
            while alpha < angle + 0.3:  # TODO: Scale this value with battery voltage level (0.3 - 1.0)
                new_pos = self.motor_sensor.beyblade(150)
                delta_pos = (new_pos[0] - old_pos[0], new_pos[1] - old_pos[1])
                old_pos = new_pos
                alpha = alpha + (delta_pos[1] - delta_pos[0]) / constants.AXLE_LENGTH * 0.05
                print(self.color_sensor.get_color_name())
                if (self.color_sensor.get_color_hls()[1] < 100
                        and alpha > angle - 0.5
                        and self.color_sensor.get_color_name() == "black"):
                    directions.append(Direction(360 - 90 * i))
                    print("path detected")
                    break

        print(f"scan_node: {directions}")
        self.motor_sensor.stop()
        print("scan_node: done!")

        print("Correct base heading")
        self.motor_sensor.turn_angle_blocking(-80, 50)

        return directions
