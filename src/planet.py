#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from enums import Color
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

path_list = Dict[Tuple[int, int], Dict[Direction, Tuple[Optional[Tuple[int, int]], Direction, Weight]]]


class DijkstraPath:
    def __init__(self, destination, weight, start, direction_destination, direction_start):
        self.destination: Tuple[int, int] = destination
        self.weight: weight = weight
        self.start: Tuple[int, int] = start
        self.direction_destination: Direction = direction_destination
        self.direction_start: Direction = direction_start

    def update_weight(self, new_weight: int):
        self.weight = new_weight


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self):
        """ Initializes the data structure """
        self.paths: path_list = {}
        self.nodes: Dict[Tuple[int, int], Color] = {}
        self.possible_open_nodes: List[Tuple[int, int]] = []
        self.planet_name = ""

    # add unexplored path
    def add_unexplored_path(self, start: Tuple[Tuple[int, int], Direction]):
        # Store unexplored path with end coordinates as None
        if start[0] not in self.paths:
            print("P-59:")
            print(start[0])
            self.paths[start[0]] = {}

        if start[1] not in self.paths[start[0]]:
            self.paths[start[0]][Direction(start[1])] = (None, Direction.NORTH, -69420)
            print("add_unexplored_path executed")

    # adds unexplored paths from a list
    def add_unexplored_node(self, position: Tuple[int, int], color: Color, directions: [Direction]):

        self.add_node(position, color)

        for direction in directions:
            print(f"Added direction: {direction}")
            self.add_unexplored_path((position, direction))

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
            print("P-101:")
            print(start[0])
            self.paths[start[0]] = {}
            if start[0] not in self.possible_open_nodes:
                self.possible_open_nodes.append(start[0])

        self.paths[start[0]][Direction(start[1])] = (target[0], target[1], weight)
        if target[0] not in self.paths:
            print("P-106:")
            print(target[0])
            self.paths[target[0]] = {}
            if target[0] not in self.possible_open_nodes:
                self.possible_open_nodes.append(target[0])
        self.paths[target[0]][Direction(target[1])] = (start[0], start[1], weight)

        if start[0] in self.paths.keys() and len(self.paths[start[0]].keys()) == 4:
            self.add_node(start[0], self.get_node_color(start[0]))
            if start[0] in self.possible_open_nodes:
                self.possible_open_nodes.remove(start[0])

        if target[0] in self.paths.keys() and len(self.paths[target[0]].keys()) == 4:
            self.add_node(target[0], self.get_node_color(target[0]))
            if target[0] in self.possible_open_nodes:
                self.possible_open_nodes.remove(target[0])

    # stores a node with its color
    def add_node(self, coordinates: Tuple[int, int], color: Color):
        self.nodes[coordinates] = color
        print(f"added node {coordinates} to known nodes")
        if coordinates not in self.paths:
            print("P-115:")
            print(coordinates)
            self.paths[coordinates] = {}

        if coordinates in self.possible_open_nodes:
            self.possible_open_nodes.remove(coordinates)

    # checks if the node color is the expected one
    def check_node(self, coordinates: Tuple[int, int], color: Color) -> bool:
        return self.nodes[coordinates] and self.nodes[coordinates] == color

    # calculates the color of the node based on collected data
    def get_node_color(self, coordinates: Tuple[int, int]) -> Color:
        if len(self.nodes.keys()) == 0:
            return Color.RED
        check_key = list(self.nodes.keys())[0]
        check_color = self.nodes[check_key]
        opposite_color = Color.BLUE if check_color == Color.RED else Color.RED
        check_sum = (check_key[0] + check_key[1]) % 2
        coordinates_sum = (coordinates[0] + coordinates[1]) % 2
        return check_color if coordinates_sum == check_sum else opposite_color

    # checks if given color should be at given coordinate
    def check_node_color(self, coordinates: Tuple[int, int], color: Color) -> bool:
        nc = self.get_node_color(coordinates)
        print(f"predicted node color: {nc}")
        return color == nc

    def get_rotations(self, coordinates: Tuple[Tuple[int, int], Direction], direction: Direction) -> int:
        current_dir = coordinates[1]
        i: int = 1
        while current_dir != direction:
            current_dir = Direction((current_dir.value - 90) % 360)
            if current_dir in self.paths[coordinates[0]].keys():
                i += 1
        return i

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

        if start == target:
            return []

        # return none if start or target are not nodes or if start is target
        if start not in self.paths or target not in self.paths:
            return None

        # get most efficient paths to every node
        final_paths: Dict[Tuple[int, int], DijkstraPath] = self.dijkstra_final_paths(start)

        if target not in final_paths:
            return None

        return self.extract_path_from_dijkstra(final_paths, start, target)

    @staticmethod
    def extract_path_from_dijkstra(distances: Dict[Tuple[int, int], DijkstraPath],
                                   start: Tuple[int, int], target: Tuple[int, int]) -> List[
                                    Tuple[Tuple[int, int], Direction]]:
        # reconstruct most efficient path to destination
        return_path: List[Tuple[Tuple[int, int], Direction]] = []
        return_path.insert(0, (distances[target].start, distances[target].direction_start))

        # backtrack from target to start in finial paths
        while return_path[0][0] != start:
            last_element = return_path[0][0]
            return_path.insert(0, (distances[last_element].start,
                                   distances[last_element].direction_start))

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
            for option in options.copy():
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
            for option in new_options:
                if option.destination not in final_paths or option.weight < final_paths[option.destination].weight:
                    options.append(option)

        return final_paths

    def get_unexplored_paths(self) -> List[DijkstraPath]:
        unexplored_paths: List[DijkstraPath] = []
        for node_position, node_directions in self.paths.items():
            for direction, path in node_directions.items():
                if path[0] is None:
                    unexplored_paths.append(DijkstraPath(path[0], path[2], node_position, path[1], direction))

        for node in self.possible_open_nodes:
            unexplored_paths.append(DijkstraPath(None, -69420, node, None, None))

        return unexplored_paths

    def explore_next(self, distances: Dict[Tuple[int, int], DijkstraPath], current_position: Tuple[int, int],
                     current_direction: Direction) -> Optional[Tuple[Tuple[int, int], Direction]]:

        # find unexplored paths
        unexplored_paths: List[DijkstraPath] = self.get_unexplored_paths()

        # return None if no unexplored paths are found
        if len(unexplored_paths) == 0:
            return None

        # find closest (minimum weight) nodes with unexplored path
        distances[current_position] = DijkstraPath(current_position, 0, current_position, Direction.NORTH,
                                                   Direction.NORTH)
        min_distance_paths: List[tuple[int, DijkstraPath]] = []

        for path in unexplored_paths.copy():
            if path.start not in distances.keys():
                unexplored_paths.remove(path)

        if len(unexplored_paths) == 0:
            return None

        for path in unexplored_paths:
            if len(min_distance_paths) == 0:
                min_distance_paths.append((distances[path.start].weight, path))
            elif distances[path.start].weight < distances[min_distance_paths[0][1].start].weight:
                min_distance_paths = [(distances[path.start].weight, path)]
            elif distances[path.start].weight == distances[min_distance_paths[0][1].start].weight:
                min_distance_paths.append((distances[path.start].weight, path))

        # return if only one path is found
        if len(min_distance_paths) == 1:
            return min_distance_paths[0][1].start, min_distance_paths[0][1].direction_start

        # if current node has unexplored paths, select path with the least rotational difference
        if min_distance_paths[0][1].start == current_position:
            minimum_rotation = 360
            selected_path = min_distance_paths[0][1]
            for weight, path in min_distance_paths:
                rotation = abs(path.direction_start - current_direction)
                if rotation < minimum_rotation:
                    selected_path = path
                    minimum_rotation = rotation

            return selected_path.start, selected_path.direction_start

        # TODO smart decision which path is taken
        """
        options:
            - Decide over min rotation on arrival
            - Decide on departure min rotation
            - Decide on path with least unexplored paths nearby (complicated)
        """
        return min_distance_paths[0][1].start, min_distance_paths[0][1].direction_start

    # returns first step towards target
    def get_next_node(self, current_position: tuple[tuple[int, int], Direction],
                      target: Optional[tuple[int, int]]) -> Optional[tuple[tuple[int, int], Direction]]:
        # calculate distance to all nodes from current_position
        distances: Dict[Tuple[int, int], DijkstraPath] = self.dijkstra_final_paths(current_position[0])

        if target is not None and target in distances:
            # calculate path to target
            path = self.extract_path_from_dijkstra(distances, current_position[0], target)

            # return first step of path if path exists
            if path is not None:
                return path[0]

        # get next node to explore
        explore_node = self.explore_next(distances, current_position[0], current_position[1])
        print(f"explore_node: {explore_node}")

        if explore_node is None:
            return None

        if explore_node[0] == current_position[0]:
            return explore_node

        # get path to  explore_node
        next_path = self.extract_path_from_dijkstra(distances, current_position[0], explore_node[0])

        if next_path is None:
            return None
        else:
            return next_path[0]


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
