import time
from typing import Tuple

from odometry import Odometry
from planet import Planet, Direction
from follow import Follow
from sensors.touch_sensor import TouchSensor
from sensors.sonar_sensor import SonarSensor
from sensors.speaker_sensor import SpeakerSensor
from sensors.color_sensor import ColorSensor
from enums import StopReason, PathStatus, NodeColor
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
        self.planet.group3mode = True

        self.is_first_node = True
        self.node_scan_done = False

        # Exploration
        self.__next_path: Tuple[Tuple[int, int], Direction] = None
        self.current_target: Tuple[int, int] = None
        self.current_node_color: NodeColor = None
        self.detected_collision = False
        self.__start_position: Tuple[Tuple[int, int], int] = None  # Update data structure

    def update_next_path(self, direction: Direction):
        print(">>>>>>>  >>>> >> Received update for direction")
        self.__next_path = ((self.__next_path[0], self.__next_path[1]), direction)

    def set_current_target(self, target: Tuple[int, int]):
        self.current_target = target

    def set_start_position(self, start_x: int, start_y: int, start_direction: Direction):
        self.__start_position = ((start_x, start_y), start_direction)

        # 1. Memo target
        # 2. If current node == target?
        # 3. If not => Check if target is already discovered -> Calculate the shortest path =>  drive to target
        # 4. If not continue exploring
        #
        # Check on each node if the target is reached; handle target override

    def is_node_target(self, current_position):
        if self.current_target is None:
            return False

        return current_position[0][0] == self.current_target[0] and current_position[0][1] == self.current_target[1]

    def handle_node(self, current_position: Tuple[Tuple[int, int], int]):

        print("Handle node")
        # Check if current node is target node TODO: Impl helper function for comparison
        if self.is_node_target(current_position):
            print("Node handling: Current node is target")
            # send path message with last driven path
            self.communication.send_path(self.planet.planet_name, self.start_position[0][0], self.start_position[0][1],
                                         self.start_position[1], current_position[0], current_position[1],
                                         current_position[2], PathStatus.FREE)  # TODO: Check how you address tuples?
            self.communication.send_target_reached("Target reached!")

        if self.is_first_node:
            print("First node detected \n")
            self.communication.send_ready()
            self.is_first_node = False
        else:
            path_status = PathStatus.FREE if not self.detected_collision else PathStatus.BLOCKED
            print(f"Path status: {path_status}")

            # send path message with last driven path
            self.communication.send_path(self.planet.planet_name, self.start_position[0][0], self.start_position[0][1],
                                         self.start_position[1], current_position[0][0], current_position[0][1],
                                         current_position[1], path_status)

        print("Start node scanning \n")
        scanned_directions = self.follow.scan_node()
        print(f"Scanned directions: {scanned_directions}")
        self.planet.add_unexplored_node(current_position[0], self.current_node_color, scanned_directions)
        print(f"Get_Paths: {self.planet.get_paths()}")
        print(f"Current position: {current_position}")
        print("Node scan done!")
        self.detected_collision = False

    def add_path(self, start, target, weight):
        self.planet.add_path(start, target, weight)

    def play_tone(self):
        self.speaker_sensor.play_tone()

    def robot(self):

        # Initialize communication, configure, connect, etc.
        # ...
        # Set current planet for mothership
        planet_name = input('Enter the test planet name and wait for response:')
        msg = '{"from":"client","type":"testPlanet","payload":{{"planetName":"' + planet_name + '"}}'
        self.communication.client.publish("explorer/<GROUP>", payload=msg, qos=2)

        # print("Press button to start exploration")

        while not self.button.is_pressed():
            continue

        # self.color_sensor.calibrate_hls()
        print(" ")
        print("")
        time.sleep(5)

        print("Starting exploration...")

        # TODO: Impl color calibration before running

        while self.active:
            stop_reason = self.follow.follow()
            self.follow.stop()
            self.speaker_sensor.play_tone()

            if stop_reason is StopReason.COLLISION:
                self.follow.turn_until_line_detected()
                self.detected_collision = True
            elif stop_reason is StopReason.NODE:
                print("Node detected")
                self.current_node_color = NodeColor(self.color_sensor.get_hls_color_name())
                self.motor_sensor.stop()
                self.odometry.update_position(self.motor_sensor.motor_positions)
                current_position = self.odometry.get_coordinates()
                print("Odometry updated")
                print("")
                print(f"Current position: {self.odometry.get_coordinates()}")
                print("")

                self.handle_node(current_position)

                # Wait for path unveiled
                print("Wait for 'path unveiled' message")
                time.sleep(3)  # Check if we can receive messages while sleeping
                print("")

                # Handle exploration
                # TODO: Find a better name for next_position
                print("Find next direction")
                self.__next_path = self.planet.explore_next(current_position[0],
                                                            current_position[1])  # TODO: Update data structure

                print(f"self.__next_path: {self.__next_path}")
                # if next_position is node, the whole map is explored
                if self.__next_path is None:
                    # Whole map explored
                    if self.current_target is None:
                        print("No target found")
                        print("Ending mission")
                        break  # Send exploration complete; no target

                    path_2_target = self.planet.get_to_target(current_position, self.current_target)
                    if path_2_target is None:
                        print("Target not on planet")
                        print("Ending exploration")
                        # Send target is not on map
                        # Exploration complete
                        break

                    self.__next_path = path_2_target
                    print("Going to the next path", self.__next_path)

                print("")
                print("Send path select")
                self.communication.send_path_select(self.planet.planet_name, self.__next_path[0][0],
                                                    self.__next_path[0][1],
                                                    self.__next_path[1].value)

                print("")
                # wait for response
                print("Wait for path correction")
                time.sleep(3)  # DOES THIS WORK???????????????????????????????????????????
                # may correct direction (see communication)

                self.start_position = current_position
                print("Update start position")
            else:
                raise NotImplementedError("Unknown stop")

            # Handle direction alignment
            if not self.detected_collision:  # TODO: Improve this remove
                print(self.__next_path, self.__next_path[1].value)
                turn_angle = (self.start_position[1] -
                              self.__next_path[1].value) if self.__next_path[1].value > 180 else (
                              self.__next_path[1].value)
                self.motor_sensor.turn_angle_blocking(turn_angle)

        # Mission done
        # TODO: CHECK WHEN WE NEED TO SEND EXPLOR_COMPL OR TARGET_REACHED
        # self.communication.send_exploration_complete("Planet fully discovered!")
