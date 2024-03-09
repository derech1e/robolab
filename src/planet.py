#!/usr/bin/env python3
import math
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


# class Vertex:
#     def __init__(self, xy: Tuple[int, int], direction: Direction, weight: int):
#         self.xy = xy
#         self.direction = direction
#         self.weight = weight
#

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

    # TODO: Impl better type for remaining_paths
    def find_lowest_weight_vertex(self, remaining_paths: [], distance_map: Dict[any, float]):
        current_min_weight = math.inf
        current_min_vertex = None

        for vertex in remaining_paths:
            weight = distance_map[vertex]
            if weight < current_min_weight:
                current_min_vertex = vertex
                current_min_weight = weight
        return current_min_vertex

    def dijkstra(self, start: Tuple[int, int], target: Tuple[int, int]):
        remaining_paths = []
        # Use two objects to easily access individual vertices
        distance_map = {}  # Saves the distance for each vertex
        previous_vertex_map = {}  # Saves the previous vertex for each vertex
        path = []

        # Structure
        # (Vertex, Direction, Weight)
        # Iterate over all node and set them to infinity distance
        for vertex in self.paths.keys():
            distance_map[vertex] = math.inf  # Set current distance to max
            previous_vertex_map[vertex] = None  # Set previous vertex to None
            remaining_paths.append(vertex)  # Add the vertex to the working array of remaining paths

        print(remaining_paths)
        distance_map[start] = 1

        while remaining_paths:
            lowest_weight_vertex = self.find_lowest_weight_vertex(remaining_paths,
                                                                  distance_map)  # Select lowest weight of remaining_paths
            print(lowest_weight_vertex)
            remaining_paths.remove(lowest_weight_vertex)  # Remove the paths from remaining paths

            if lowest_weight_vertex == target:  # Stop the algorithm if the current vertex is the target vertex
                break  # TODO: Impl logic here

            for vertex_neighbor in self.paths[lowest_weight_vertex].values():  # for each neighbour of the current lowest vertex
                if vertex_neighbor[2] != -1:  # Check if path is blocked
                    if vertex_neighbor[0] != lowest_weight_vertex:  # Check if the lowest vertex is not the current neighbour
                        alternative_vertex = distance_map[lowest_weight_vertex] + vertex_neighbor[2]
                        if alternative_vertex < distance_map[vertex_neighbor[0]]:
                            distance_map[vertex_neighbor[0]] = alternative_vertex

                            previous_vertex_map[vertex_neighbor[0]] = (
                                lowest_weight_vertex, self.get_direction(lowest_weight_vertex, vertex_neighbor))

        # Path mapping
        weight_sum = 0
        next_target = target

        if previous_vertex_map[next_target] is not None or next_target == start:
            while previous_vertex_map[next_target]:
                weight_sum += distance_map[next_target]
                path.append(previous_vertex_map[next_target])
                next_target = previous_vertex_map[next_target][0]

        path.reverse()
        return path

    def get_direction(self, lowest_weight_vertex: Tuple[int, int], vertex_neighbor: Tuple[int, int]):
        for next_vertex in self.paths[lowest_weight_vertex]:
            if vertex_neighbor == self.paths[lowest_weight_vertex][next_vertex]:
                return next_vertex
        return Direction.NORTH
