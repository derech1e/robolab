from enum import StrEnum


class MessageType(StrEnum):
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


class MessageFrom(StrEnum):
    CLIENT = "client"
    SERVER = "server"
    DEBUG = "debug"
    SYNTAX = "syntax"


class PathStatus(StrEnum):
    FREE = "free"
    BLOCKED = "blocked"


class StopReason(StrEnum):
    COLLISION = "collision"
    NODE = "node"
    FIRST_NODE = "first_node"


class Color(StrEnum):
    BLACK = "black"
    WHITE = "white"
    BLUE = "blue"
    RED = "red"
