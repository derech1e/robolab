import time

from odometry import Odometry
from planet import Planet
from follow import Follow
from sensors.touch_sensor import TouchSensor
from sensors.sonar_sensor import SonarSensor
from sensors.speaker_sensor import SpeakerSensor
from sensors.color_sensor import ColorSensor


class Robot:

    def __init__(self, communication):

        self.button = TouchSensor()
        self.sonar_sensor = SonarSensor()
        self.speaker_sensor = SpeakerSensor()
        self.color_sensor = ColorSensor()

        self.planet = Planet()
        self.communication = communication
        self.odometry = Odometry()
        self.follow = Follow(self.color_sensor)

        self.active = True
        self.button_pressed = False
        self.should_follow = False

    def robot(self):

        print("Press button to start exploration")

        # while not self.button.is_pressed():
        #    continue

        # TODO: Impl color calibration before running

        while self.active:
            if self.sonar_sensor.is_colliding():
                self.speaker_sensor.play_tone()
                self.follow.stop()
                self.should_follow = False

            if self.should_follow and not self.follow.line_detection_in_progress:
                self.follow.follow()
            else:
                if not self.follow.line_detection_in_progress:
                    self.follow.turn_until_line_detected()
                    self.should_follow = False
