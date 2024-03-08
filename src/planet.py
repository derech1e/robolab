#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class DijkstraPath:

    def __init__(self, start_xy: Tuple[int, int], start_direction: Direction, target_xy: Tuple[int, int],
                 target_direction: Direction, weight: int):
        self.start_xy = start_xy
        self.start_direction = start_direction
        self.target_xy = target_xy
        self.target_direction = target_direction
        self.weight = weight

    def get_start_target_path(self):
        return self.target_xy, self.target_direction, self.weight

    def get_target_start_path(self):
        return self.start_xy, self.start_direction, self.weight


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self):
        """ Initializes the data structure """
        self.paths = {}

    # DO NOT EDIT THE METHOD SIGNATURE
    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

        path = DijkstraPath(start[0], start[1], target[0], target[1], weight)
        # if the Node isn't discovered yet init it with a empty object
        if path.start_xy not in self.paths:
            self.paths[path.start_xy] = {}
        if path.target_xy not in self.paths:
            self.paths[path.target_xy] = {}
        self.paths[path.start_xy][path.start_direction] = path.get_start_target_path()
        self.paths[path.target_xy][path.target_direction] = path.get_target_start_path()


    # DO NOT EDIT THE METHOD SIGNATURE
    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """
        return self.paths

    # DO NOT EDIT THE METHOD SIGNATURE
    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[
        List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: None, List[] or List[Tuple[Tuple[int, int], Direction]]
        """

        # check if a calculation of the shortest path can be done
        if target not in self.paths:
            print("Path dictionary does not contain target node")
            return None

        # return an empty array if the start is the target; no shortest path algorythm needed
        if start == target:
            return []

        return self.dijkstra(start, target)

    def dijkstra(self, start: Tuple[int, int], target: Tuple[int, int]):
        pass



