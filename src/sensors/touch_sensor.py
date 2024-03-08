from ev3dev import ev3


class TouchSensor:

    def __init__(self):
        self.touchSensor = ev3.TouchSensor()

    def value(self):
        return self.touchSensor.value()

    def is_pressed(self):
        return self.value() == 1
