import time

from odometry import Odometry
from planet import Planet
from follow import Follow
from sensors.touch_sensor import TouchSensor
from sensors.sonar_sensor import SonarSensor
from sensors.speaker_sensor import SpeakerSensor


class Robot:

    def __init__(self, communication):
        self.planet = Planet()
        self.communication = communication
        self.odometry = Odometry()
        self.follow = Follow()

        self.button = TouchSensor()
        self.sonar_sensor = SonarSensor()
        self.speaker_sensor = SpeakerSensor()

        self.active = True
        self.button_pressed = False
        self.collision_detected = False

    def robot(self):

        print("Press button to start exploration")

        #while not self.button.is_pressed():
        #    continue

        # TODO: Impl color calibration before running

        while self.active:

            if self.sonar_sensor.is_colliding() and not self.collision_detected:
                self.speaker_sensor.play_tone()
                self.follow.stop()
                self.collision_detected = True

            if not self.collision_detected and not self.follow.collision_turn_in_progress:
                self.follow.follow()
            else:
                if not self.follow.collision_turn_in_progress:
                    self.follow.turn_until_line_detected()
                    self.collision_detected = False

