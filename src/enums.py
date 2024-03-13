from enum import Enum


class MessageType(Enum):
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
    CLIENT = "client"
    SERVER = "server"
    DEBUG = "debug"
    SYNTAX = "syntax"


class PathStatus(Enum):
    FREE = "free"
    BLOCKED = "blocked"


class StopReason(Enum):
    COLLISION = "collision"
    NODE = "node"


class NodeColor(Enum):
    BLUE = "blue"
    RED = "red"
