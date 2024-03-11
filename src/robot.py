import time
from typing import Tuple

from odometry import Odometry
from planet import Planet, Direction
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
        self.communication.set_robot(self)
        self.odometry = Odometry()
        self.follow = Follow(self.color_sensor)

        self.active = True
        self.should_follow = False

        self.is_first_node = True
        self.node_scan_done = False

        # Exploration
        self.__next_targeted_path: Tuple[Tuple[int, int], Direction] = None
        self.current_target: Tuple[int, int] = None

    def is_red_or_blue(self, color):
        return color == "red" or color == "blue"

    def set_next_targeted_path(self, target: Tuple[Tuple[int, int], Direction]):
        self.__next_targeted_path = target

    def update_target_direction(self, direction: Direction):
        self.__next_targeted_path = ((self.__next_targeted_path[0], self.__next_targeted_path[1]), direction)

    def set_current_target(self, target: Tuple[int, int]):
        # 1. Memo target
        # 2. If current node == target?
        # 3. If not => Check if target is already discovered -> Calculate shortest path =>  drive to target
        # 4. If not continue exploring
        #
        # Check on each node if the target is reached; handle target override
        self.current_target = target

    def handle_node(self):
        if self.is_first_node:
            self.communication.send_ready()
            self.is_first_node = False
            return



    def add_path(self, start, target, weight):
        self.planet.add_path(start, target, weight)

    def play_tone(self):
        self.speaker_sensor.play_tone()


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

            # If node scan in progress
            # break

            # If collision rotation in progress
            # break

            # Waiting for response after node scan
            # time.sleep(6)



            if self.is_red_or_blue(self.color_sensor.get_hls_color_name()) and not self.node_scan_done:
                self.handle_node()
                self.should_follow = False
                self.follow.stop()
                print("Color detected!")
                time.sleep(2)
                self.follow.scan_node()
                self.node_scan_done = True

        if self.should_follow and not self.follow.line_detection_in_progress:
            self.follow.follow()
        else:
            if not self.follow.line_detection_in_progress:
                self.follow.turn_until_line_detected()
                self.should_follow = False

        # Mission done
        #self.communication.send_complete() # TODO: Check if this can stay in comms
