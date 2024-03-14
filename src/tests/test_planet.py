#!/usr/bin/env python3

import unittest
from src.planet import Direction, Planet, Color
import random


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        self.nodes = [
            (((0, 0), Direction.EAST), ((1, 1), Direction.WEST), 1),
            (((0, 0), Direction.SOUTH), ((0, 1), Direction.NORTH), 3),
            (((0, 1), Direction.SOUTH), ((0, 3), Direction.NORTH), 1),
            (((0, 3), Direction.EAST), ((3, 2), Direction.NORTH), 1),
            (((1, 1), Direction.NORTH), ((4, 1), Direction.NORTH), 3),
            (((1, 1), Direction.EAST), ((2, 1), Direction.WEST), 2),
            (((1, 1), Direction.SOUTH), ((3, 3), Direction.WEST), 5),
            (((2, 1), Direction.NORTH), ((2, 1), Direction.NORTH), 1),
            (((2, 1), Direction.EAST), ((4, 1), Direction.WEST), 1),
            (((2, 1), Direction.SOUTH), ((3, 2), Direction.WEST), 3),
            (((3, 2), Direction.EAST), ((4, 1), Direction.SOUTH), 1),
            (((3, 2), Direction.SOUTH), ((3, 3), Direction.NORTH), 4),
            (((3, 3), Direction.EAST), ((4, 1), Direction.EAST), 4),
        ]
        # Initialize your data structure here
        self.planet = Planet()
        for node in self.nodes:
            if node[0][0][0] + node[0][0][1] % 2 == 0:
                self.planet.add_node(node[0][0], Color.RED)
            else:
                self.planet.add_node(node[0][0], Color.BLUE)
            if node[1][0][0] + node[1][0][1] % 2 == 0:
                self.planet.add_node(node[1][0], Color.RED)
            else:
                self.planet.add_node(node[1][0], Color.BLUE)
            self.planet.add_path(node[0], node[1], node[2])
        self.planet.add_unexplored_path(((0, 0), Direction.WEST))

        self.p2 = Planet()
        # (0,1)---5---(1,1)---1---(2,1)
        #   |           |
        #   1           6
        #   |           |
        # (0,0)---1---(1,0)
        self.p2.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.p2.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.p2.add_path(((0, 1), Direction.EAST), ((1, 1), Direction.WEST), 5)
        self.p2.add_path(((1, 0), Direction.NORTH), ((1, 1), Direction.SOUTH), 6)
        self.p2.add_path(((1, 1), Direction.EAST), ((2, 1), Direction.WEST), 1)

        self.p3 = Planet()
        # (0,0)---2---(0,1)---2---(0,2)
        #                |
        #                1
        #                |
        #               / \
        #               \_/
        self.p3.add_path(((0, 0), Direction.EAST), ((0, 1), Direction.WEST), 2)
        self.p3.add_path(((0, 1), Direction.EAST), ((0, 2), Direction.WEST), 2)
        self.p3.add_path(((0, 1), Direction.SOUTH), ((0, 1), Direction.SOUTH), 1)

        self.p4 = Planet()
        #    |
        # -(0,0)---1---(1, 0)-
        #    |
        #    2
        #    |
        #  (0,1)-
        #    |
        self.p4.add_node((0, 0), Color.RED)
        self.p4.add_node((0, 1), Color.BLUE)
        self.p4.add_node((1, 0), Color.BLUE)
        self.p4.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.p4.add_path(((0, 0), Direction.SOUTH), ((0, 1), Direction.NORTH), 2)
        self.p4.add_unexplored_path(((0, 1), Direction.SOUTH))
        self.p4.add_unexplored_path(((1, 0), Direction.EAST))
        self.p4.add_unexplored_path(((0, 0), Direction.WEST))
        self.p4.add_unexplored_path(((0, 0), Direction.WEST))

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        path = self.planet.get_paths()
        self.assertEqual(type(path), dict)
        self.assertEqual(type(list(path.keys())[0]), tuple)
        self.assertEqual(type(list(path.keys())[0][0]), int)
        test_key = list(path.keys())[0]
        test_data = path[test_key]
        self.assertEqual(type(test_data), dict)
        test_key = list(test_data.keys())[0]
        self.assertEqual(type(test_key), Direction)
        test_data = test_data[test_key]
        self.assertEqual(type(test_data), tuple)
        self.assertEqual(type(test_data[0]), tuple)
        self.assertEqual(type(test_data[1]), Direction)
        self.assertEqual(type(test_data[2]), int)
        self.assertEqual(type(test_data[0][0]), int)

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.assertEqual(Planet().get_paths(), {})

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        target_shortest_path = [((0, 0), Direction.NORTH), ((0, 1), Direction.EAST), ((1, 1), Direction.EAST)]
        self.assertEqual(target_shortest_path, self.p2.shortest_path((0, 0), (2, 1)))

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (-1, -1)))

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        self.assertIn(self.planet.shortest_path((0, 0), (3, 2)), [
            [((0, 0), Direction.EAST), ((1, 1), Direction.EAST), ((2, 1), Direction.EAST), ((4, 1), Direction.SOUTH)],
            [((0, 0), Direction.EAST), ((1, 1), Direction.NORTH), ((4, 1), Direction.SOUTH)],
            [((0, 0), Direction.SOUTH), ((0, 1), Direction.SOUTH), ((0, 3), Direction.EAST)]
        ])

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        self.assertEqual(self.p3.shortest_path((0, 0), (0, 2)),
                         [((0, 0), Direction.EAST), ((0, 1), Direction.EAST)])

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (2, 0)))

    def test_speed(self):
        """
        This test should run a large amount of interations of the shortest-path algorithm to determine its speed
        """
        test_count: int = 1_000
        nodes = list(self.planet.paths.keys())
        for _ in range(test_count):
            start, target = random.choices(nodes, k=2)
            self.planet.shortest_path(start, target)

    def test_exploration(self):
        """
        This test should test if the correct explore option is recommended
        """
        start_node = (0, 0)
        start_direction = Direction.SOUTH
        distances = self.p4.dijkstra_final_paths(start_node)
        self.assertIn(self.p4.explore_next(distances, start_node, start_direction), [((0, 0), Direction.WEST),
                                                                      ((0, 0), Direction.WEST)])


if __name__ == "__main__":
    unittest.main()
