#!/usr/bin/env python3

import unittest
from src.planet import Direction, Planet


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        # Initialize your data structure here

        self.empty_planet = Planet()

        self.planet = Planet()
        # (0,1)---5---(1,1)---1---(2,1)
        #   |           |
        #   1           6
        #   |           |
        # (0,0)---1---(1,0)

        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((0, 1), Direction.EAST), ((1, 1), Direction.WEST), 5)
        self.planet.add_path(((1, 0), Direction.NORTH), ((1, 1), Direction.SOUTH), 6)
        self.planet.add_path(((1, 1), Direction.EAST), ((2, 1), Direction.WEST), 1)

        self.unreachable_path_planet = Planet()
        # (0,1)---5---(1,1)             --(2,1)---
        #   |           |               |        |
        #   1           6               |---1----|
        #   |           |
        # (0,0)---1---(1,0)
        self.unreachable_path_planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.unreachable_path_planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.unreachable_path_planet.add_path(((0, 1), Direction.EAST), ((1, 1), Direction.WEST), 5)
        self.unreachable_path_planet.add_path(((1, 0), Direction.NORTH), ((1, 1), Direction.SOUTH), 6)
        # self.unreachable_path_planet.add_path(((2, 1), Direction.EAST), ((2, 1), Direction.WEST), 1)

        self.blocked_path_planet = Planet()

        #   (0,2)---1--XXX----|
        #                     |
        #                   (4,1)-------2-----(5,1)-----1------|
        #                     |                 |              |
        #   (0,0)------2------|                 |            (6,0)
        #     |                                 |
        #     |---------1-----XXX---------------|

        self.blocked_path_planet.add_path(((0, 0), Direction.EAST), ((4, 1), Direction.SOUTH), 2)
        self.blocked_path_planet.add_path(((0, 0), Direction.SOUTH), ((5, 1), Direction.SOUTH), 1)
        self.blocked_path_planet.add_path(((4, 1), Direction.NORTH), ((0, 2), Direction.EAST), 1)
        self.blocked_path_planet.add_path(((4, 1), Direction.EAST), ((5, 1), Direction.WEST), 2)
        self.blocked_path_planet.add_path(((5, 1), Direction.EAST), ((6, 0), Direction.NORTH), 2)

        self.planet_path_loop = Planet()
        #
        #                   |---1--|
        #                   |      |
        #   (0,0)----1----(1,0)----|
        #     |             |
        #     |------1------|
        #
        self.planet_path_loop.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet_path_loop.add_path(((0, 0), Direction.SOUTH), ((1, 0), Direction.SOUTH), 1)
        self.planet_path_loop.add_path(((1, 0), Direction.NORTH), ((1, 0), Direction.EAST), 1)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        paths = self.planet.get_paths()
        planet_structure = {
            (0, 0): {
                Direction.NORTH: ((0, 1), Direction.SOUTH, 1),
                Direction.EAST: ((1, 0), Direction.WEST, 1)
            },
            (0, 1): {
                Direction.EAST: ((1, 1), Direction.WEST, 5),
                Direction.SOUTH: ((0, 0), Direction.NORTH, 1)
            },
            (1, 0): {
                Direction.NORTH: ((1, 1), Direction.SOUTH, 6),
                Direction.WEST: ((0, 0), Direction.EAST, 1)
            },
            (1, 1): {
                Direction.EAST: ((2, 1), Direction.WEST, 1),
                Direction.WEST: ((0, 1), Direction.EAST, 5),
                Direction.SOUTH: ((1, 0), Direction.NORTH, 6)
            },
            (2, 1): {
                Direction.WEST: ((1, 1), Direction.EAST, 1),
            }
        }
        self.assertEqual(paths, planet_structure)

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.assertEqual(self.empty_planet.get_paths(), {})

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        # Start: (0,0)
        # Target: (2,1)
        target_shortest_path = [((0, 0), Direction.NORTH), ((0, 1), Direction.EAST), ((1, 1), Direction.EAST)]
        self.assertEqual(self.planet.shortest_path((0, 0), (2, 1)), target_shortest_path)

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.assertIsNone(self.unreachable_path_planet.shortest_path((0, 0), (2, 1)))

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        target_shortest_path = [((0, 0), Direction.EAST)]
        self.assertEqual(target_shortest_path, self.planet_path_loop.shortest_path((0, 0), (1, 0)))

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        # TODO: Add further checks
        target_shortest_path = [((1, 0), Direction.WEST)]
        self.assertEqual(target_shortest_path, self.planet_path_loop.shortest_path((1, 0), (0, 0)))

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet_path_loop.shortest_path((1, 0), (4, 3)))


if __name__ == "__main__":
    unittest.main()
