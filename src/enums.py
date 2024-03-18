from enum import Enum


class MessageType(Enum):
    """
    This class contains all possible message types
    """
    TEST_PLANET = "testPlanet"
    READY = "ready"
    PLANET = "planet"
    PATH = "path"
    PATH_SELECT = "pathSelect"
    PATH_UNVEILED = "pathUnveiled"
    TARGET = "target"
    TARGET_REACHED = "targetReached"
    EXPLORATION_COMPLETE = "explorationCompleted"
    DONE = "done"
    SYNTAX = "syntax"
    ERROR = "error"
    NOTICE = "notice"
    ADJUST = "adjust"


class MessageFrom(Enum):
    """
    This class contains all possible options where a message can be from
    """
    CLIENT = "client"
    SERVER = "server"
    DEBUG = "debug"
    SYNTAX = "syntax"


class PathStatus(Enum):
    """
    This class contains all possible path status
    """
    FREE = "free"
    BLOCKED = "blocked"


class StopReason(Enum):
    """
    This class contains all possible stop reasons of the robot
    """
    COLLISION = "collision"
    NODE = "node"
    FIRST_NODE = "first_node"


class Color(Enum):
    """
    This class contains all processed colors
    """
    BLACK = "black"
    WHITE = "white"
    BLUE = "blue"
    RED = "red"
    NONE = "none"
