import time
from typing import Tuple

from odometry import Odometry
from planet import Planet, Direction
from follow import Follow
from sensors.touch_sensor import TouchSensor
from sensors.sonar_sensor import SonarSensor
from sensors.speaker_sensor import SpeakerSensor
from sensors.color_sensor import ColorSensor
from enums import StopReason, PathStatus
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
        self.__next_path: Tuple[Tuple[int, int], Direction] = None
        self.current_target: Tuple[int, int] = None
        self.detected_collision = False
        self.start_position: Tuple[Tuple[int, int], int] = None  # Update data structure

    def update_next_path(self, direction: Direction):
        self.__next_path = ((self.__next_path[0], self.__next_path[1]), direction)

    def set_current_target(self, target: Tuple[int, int]):
        self.current_target = target

        # 1. Memo target
        # 2. If current node == target?
        # 3. If not => Check if target is already discovered -> Calculate the shortest path =>  drive to target
        # 4. If not continue exploring
        #
        # Check on each node if the target is reached; handle target override

    def handle_node(self, current_position: Tuple[Tuple[int, int], int]):

        # Check if current node is target node TODO: Impl helper function for comparison
        if current_position[0][0] == self.current_target[0] and current_position[0][1] == self.current_target[1]:
            # send path message with last driven path
            self.communication.send_path(self.planet.planet_name, self.start_position[0][0], self.start_position[0][1],
                                         self.start_position[1], current_position[0], current_position[1],
                                         current_position[2], PathStatus.FREE)  # TODO: Check how you address tuples?
            self.communication.send_target_reached("Target reached!")

        if self.is_first_node:
            self.communication.send_ready()
            self.is_first_node = False
            return
        else:
            self.path_status = PathStatus.FREE if self.detected_collision else PathStatus.BLOCKED

            # send path message with last driven path
            self.communication.send_path(self.planet.planet_name, self.start_position[0], self.start_position[1],
                                         self.start_position[2], current_position[0], current_position[1],
                                         current_position[2], self.path_status)

        self.follow.scan_node()  # TODO: Is the node scan on the first node necessary?
        self.detected_collision = False

    def add_path(self, start, target, weight):
        self.planet.add_path(start, target, weight)

    def play_tone(self):
        self.speaker_sensor.play_tone()

    def robot(self):

        print("Press button to start exploration")

        # while not self.button.is_pressed():
        #    continue

        self.color_sensor.calibrate_hls()

        # TODO: Impl color calibration before running

        while self.active:
            stop_reason = self.follow.follow()
            self.follow.stop()
            self.speaker_sensor.play_tone()

            if stop_reason is StopReason.COLLISION:
                self.follow.turn_until_line_detected()
                self.detected_collision = True
            elif stop_reason is StopReason.NODE:

                self.motor_sensor.stop()
                self.odometry.update_position(self.motor_sensor.motor_positions)
                current_position = self.odometry.get_coordinates()
                print(self.odometry.get_coordinates())

                self.handle_node(current_position)

                # Wait for path unveiled
                time.sleep(4)  # Check if we can receive messages while sleeping

                # Handle exploration
                # TODO: Find a better name for next_position
                __next_path = self.planet.explore_next(current_position[0],
                                                       current_position[1])  # TODO: Update data structure

                # if next_position is node, the whole map is explored
                if __next_path is None:
                    # Whole map explored
                    if self.current_target is None:
                        break  # Send exploration complete; no target

                    path_2_target = self.planet.get_to_target(current_position, self.current_target)
                    if path_2_target is None:
                        # Send target is not on map
                        # Exploration complete
                        break

                    __next_path = path_2_target

                self.communication.send_path_select(self.planet.planet_name, __next_path[0][0], __next_path[0][1],
                                                    __next_path[1].value)

                # wait for response
                time.sleep(3)  # DOES THIS WORK???????????????????????????????????????????
                # may correct direction (see communication)

                self.start_position = current_position
            else:
                raise NotImplementedError("Unknown stop")

            # Handle direction alignment
            self.motor_sensor.turn_angle_blocking(self.__next_path[1].value)

        # Mission done
        # TODO: CHECK WHEN WE NEED TO SEND EXPLOR_COMPL OR TARGET_REACHED
        # self.communication.send_exploration_complete("Planet fully discovered!")
