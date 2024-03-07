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


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self):
        """ Initializes the data structure """
        self.paths: path_list = {}

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

        # TODO add reverse path ?when possible (not if server sends paths on new node)
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

        # YOUR CODE FOLLOWS (remove pass, please!)

        # {destination_node: path_to_node}
        fin_paths: Dict[Tuple[int, int], DijkstraPath] = {}
        options: List[DijkstraPath] = []

        # return none if start or target are not nodes or if start is target
        if start not in self.paths or target not in self.paths or start is target:
            return None

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
            if selected.destination in fin_paths:
                if selected.weight < fin_paths[selected.destination].weight:
                    difference = fin_paths[selected.destination].weight - selected.weight
                    fin_paths = update_paths(selected, difference, fin_paths)

            # push selected to final paths
            fin_paths[selected.destination] = selected

            # get options of selected destination
            new_options = extract_options(selected.destination, selected.weight, self.paths[selected.destination])

            # add only unvisited or more efficient options
            while new_options:
                option = new_options.pop()
                if option.destination not in fin_paths or option.weight < fin_paths[option.destination].weight:
                    options.append(option)

            options.extend(new_options)

        if target not in fin_paths:
            return None

        # reconstruct most efficient path to destination
        return_path = []
        return_path.insert(0, (fin_paths[target].start, fin_paths[target].direction_start))

        # backtrack from target to start in finial paths
        while return_path[0][0] != start:
            last_element = return_path[0][0]
            return_path.insert(0, (fin_paths[last_element].start,
                                   fin_paths[last_element].direction_start))

        return return_path


class DijkstraPath:
    def __init__(self, destination, weight, start, direction_destination, direction_start):
        self.destination: Tuple[int, int] = destination
        self.weight: weight = weight
        self.start: Tuple[int, int] = start
        self.direction_destination: Direction = direction_destination
        self.direction_start: Direction = direction_start

    def update_weight(self, new_weight: int):
        self.weight = new_weight


# get all outgoing paths from point with current weight added
def extract_options(point: Tuple[int, int], current_weight,
                    out_paths: Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]) -> List[DijkstraPath]:
    paths: List[DijkstraPath] = []
    for orientation, path in out_paths:
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

