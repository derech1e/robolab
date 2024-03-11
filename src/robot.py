import time
from typing import Tuple

from odometry import Odometry
from planet import Planet, Direction
from follow import Follow
from sensors.touch_sensor import TouchSensor
from sensors.sonar_sensor import SonarSensor
from sensors.speaker_sensor import SpeakerSensor
from sensors.color_sensor import ColorSensor
from enums import StopReason
from sensors.motor_sensor import MotorSensor


class Robot:

    def __init__(self, communication):

        self.button = TouchSensor()
        self.speaker_sensor = SpeakerSensor()
        self.color_sensor = ColorSensor()
        self.motor_sensor = MotorSensor()

        self.planet = Planet()
        self.communication = communication
        self.communication.set_robot(self)
        self.odometry = Odometry()
        self.follow = Follow(self.color_sensor, self.motor_sensor)

        self.active = True
        self.should_follow = False

        self.is_first_node = True
        self.node_scan_done = False

        # Exploration
        self.__next_targeted_path: Tuple[Tuple[int, int], Direction] = None
        self.current_target: Tuple[int, int] = None

    def set_next_targeted_path(self, target: Tuple[Tuple[int, int], Direction]):
        self.__next_targeted_path = target

    def update_target_direction(self, direction: Direction):
        self.__next_targeted_path = ((self.__next_targeted_path[0], self.__next_targeted_path[1]), direction)

    def set_current_target(self, target: Tuple[int, int]):
        # 1. Memo target
        # 2. If current node == target?
        # 3. If not => Check if target is already discovered -> Calculate the shortest path =>  drive to target
        # 4. If not continue exploring
        #
        # Check on each node if the target is reached; handle target override
        self.current_target = target

    def handle_node(self):

        # TODO: CHECK IF NODE IS EQUAL TO TARGET
        # TODO: if so remember to send path message with last driven path first!!!!

        if self.is_first_node:
            self.communication.send_ready()
            self.is_first_node = False
            return
        else:
            # TODO: REMOVE PASS AND IMPL
            # send path message with last driven path
            # scan node
            pass

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
            stop_reason = self.follow.follow()
            self.follow.stop()
            #self.speaker_sensor.play_tone()

            if stop_reason is StopReason.COLLISION:
                self.follow.turn_until_line_detected()
                # Memorize collision
                # Send on next node collision
            elif stop_reason is StopReason.NODE:
                self.odometry.update_position(self.motor_sensor.motor_positions)
                print(self.odometry.get_coordinates())
                self.motor_sensor.stop()
                self.handle_node()
                # Handle exploration
                # wait for response
                # may correct direction (on_message)
                # handle direction update
            else:
                raise NotImplementedError("Unknown stop")

            # Find new direction
            # Handle direction alignment

        # Mission done
        # TODO: CHECK WHEN WE NEED TO SEND EXPLOR_COMPL OR TARGET_REACHED
        #self.communication.send_exploration_complete("Planet fully discovered!")
