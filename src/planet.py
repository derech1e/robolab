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

path_list = Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]


class DijkstraPath:
    def __init__(self, destination, weight, start, direction_destination, direction_start):
        self.destination: Tuple[int, int] = destination
        self.weight: weight = weight
        self.start: Tuple[int, int] = start
        self.direction_destination: Direction = direction_destination
        self.direction_start: Direction = direction_start

    def update_weight(self, new_weight: int):
        self.weight = new_weight


class Robot:
    def __init__(self):
        self.position: tuple[int, int] = (-1, -1)
        self.rotation: Direction = Direction.NORTH


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self):
        """ Initializes the data structure """
        self.paths: path_list = {}
        self.robot: Robot = Robot()

    # add unexplored path
    def add_open_path(self, start: Tuple[Tuple[int, int], Direction]):
        # Store unexplored path with end coordinates as (-1, -1)
        if start[0] not in self.paths:
            self.paths[start[0]] = {}
        self.paths[start[0]][start[1]] = ((-1, -1), Direction.NORTH, -69420)

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

        # Initialize dict if node is not registered
        if start[0] not in self.paths:
            self.paths[start[0]] = {}
        self.paths[start[0]][start[1]] = (target[0], target[1], weight)

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
    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: None, List[] or List[Tuple[Tuple[int, int], Direction]]
        """

        # return none if start or target are not nodes or if start is target
        if start not in self.paths or target not in self.paths or start is target:
            return None

        # get most efficient paths to every node
        final_paths: Dict[Tuple[int, int], DijkstraPath] = self.dijkstra_final_paths(start)

        if target not in final_paths:
            return None

        # reconstruct most efficient path to destination
        return_path = []
        return_path.insert(0, (final_paths[target].start, final_paths[target].direction_start))

        # backtrack from target to start in finial paths
        while return_path[0][0] != start:
            last_element = return_path[0][0]
            return_path.insert(0, (final_paths[last_element].start,
                                   final_paths[last_element].direction_start))

        return return_path

    # Dijkstra algorithm known map
    def dijkstra_final_paths(self, start: Tuple[int, int]) -> Dict[Tuple[int, int], DijkstraPath]:
        # {destination_node: path_to_node}
        final_paths: Dict[Tuple[int, int], DijkstraPath] = {}
        options: List[DijkstraPath] = []

        # add outward paths of starting node
        options.extend(extract_options(start, 0, self.paths[start]))
        # dijkstra path collecting
        while options:
            # select option with the lowest weight
            dummy = DijkstraPath(-1, float("inf"), -1, -1, -1)
            selected = dummy

            for option in options:
                if option.weight < selected.weight and option.destination != start:
                    selected = option

            if selected is dummy:
                break

            # remove selected and backtracking paths from options
            for option in options:
                if selected.destination == option.destination or option.destination == start:
                    options.remove(option)

            # update paths if more efficient option is found
            if selected.destination in final_paths:
                if selected.weight < final_paths[selected.destination].weight:
                    difference = final_paths[selected.destination].weight - selected.weight
                    final_paths = update_paths(selected, difference, final_paths)

            # push selected to final paths
            final_paths[selected.destination] = selected

            # get options of selected destination
            new_options = extract_options(selected.destination, selected.weight, self.paths[selected.destination])

            # add only unvisited or more efficient options
            while new_options:
                option = new_options.pop()
                if option.destination not in final_paths or option.weight < final_paths[option.destination].weight:
                    options.append(option)

            options.extend(new_options)

        return final_paths

    def explore_next(self, current_position: Tuple[int, int],
                     current_direction: Direction) -> Tuple[Tuple[int, int], Direction]:
        # find unexplored paths
        unexplored_paths: List[DijkstraPath] = []
        for node_position, node_directions in self.paths.items():
            for direction, path in node_directions.items():
                if path[0] == (-1, -1):
                    unexplored_paths.append(DijkstraPath(path[0], path[2], node_position, path[1], direction))

        # find closest (minimum weight) nodes with unexplored path
        distances: Dict[Tuple[int, int], DijkstraPath] = self.dijkstra_final_paths(current_position)
        min_distance_paths: List[tuple[int, DijkstraPath]] = []

        for path in unexplored_paths:
            if len(min_distance_paths) == 0:
                min_distance_paths.append((distances[path.start].weight, path))
            elif distances[path.start].weight < min_distance_paths[0][1].weight:
                min_distance_paths = [(distances[path.start].weight, path)]
            elif distances[path.start].weight == min_distance_paths[0][1].weight:
                min_distance_paths.append((distances[path.start].weight, path))

        # return if only one path is found
        if len(min_distance_paths) == 1:
            return min_distance_paths[0][1].start, min_distance_paths[0][1].direction_start

        # if current node has unexplored paths, select path with the least rotational difference
        if min_distance_paths[0][1].start == current_position:
            minimum_rotation = 360
            selected_path = min_distance_paths[0][1]
            for weight, path in min_distance_paths:
                if abs(path.direction_start - current_direction) < minimum_rotation:
                    selected_path = path

            return selected_path.start, selected_path.direction_start

        # TODO smart decision which path is taken
        return min_distance_paths[0][1].start, min_distance_paths[0][1].direction_start

    # return path from current position to a target
    def path_target(self, target: tuple[int, int]) -> Optional[list[tuple[tuple[int, int], Direction]]]:
        return self.shortest_path(self.robot.position, target)


# get all outgoing paths from point with current weight added
def extract_options(point: Tuple[int, int], current_weight,
                    out_paths: Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]) -> List[DijkstraPath]:
    paths: List[DijkstraPath] = []
    for orientation, path in out_paths.items():
        if path[2] < 0:
            continue
        paths.append(DijkstraPath(path[0], path[2] + current_weight, point, path[1], orientation))
    return paths


# update all dependent paths recursively if new faster path is found
def update_paths(new_path: DijkstraPath, difference: int,
                 paths: Dict[Tuple[int, int], DijkstraPath]) -> Dict[Tuple[int, int], DijkstraPath]:
    for path_destination in paths:
        path = paths[path_destination]
        if path.start != new_path.destination:
            continue

        paths[path_destination].update_weight(path.weight - difference)
        paths = update_paths(paths[path_destination], difference, paths)

    return paths
