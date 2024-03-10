from odometry import Odometry
from planet import Planet
from follow import Follow
from sensors.touch_sensor import TouchSensor


class Robot:

    def __init__(self, communication):
        self.planet = Planet()
        self.communication = communication
        self.odometry = Odometry()
        self.follow = Follow()

        self.button = TouchSensor()

        self.active = True
        self.button_pressed = False

    def robot(self):

        print("Press button to start exploration")

        #while not self.button.is_pressed():
        #    continue

        # TODO: Impl color calibration before running

        while self.active:
            self.follow.follow()
