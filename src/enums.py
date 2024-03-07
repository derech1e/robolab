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


class MessageFrom(Enum):
    CLIENT = "client"
    SERVER = "server"
    DEBUG = "debug"


class PathStatus(Enum):
    FREE = "free"
    BLOCKED = "blocked"
