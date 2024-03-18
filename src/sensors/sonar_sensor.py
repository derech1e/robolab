import math
import time
import constants

import ev3dev.ev3 as ev3


class SonarSensor:
    """
    This class is used to control the sonar sensor of the ev3 brick
    """

    def __init__(self):
        """
        Initializes the sonar sensor and set the mode to 'US-DIST-CM' as well as the last scanned distance to infinity
        """
        self.ultraSonic = ev3.UltrasonicSensor()
        self.ultraSonic.mode = 'US-DIST-CM'  # Continuous measurement in centimeters (for inch use US-DIST-IN)
        self.last_check: int = -1
        self.prev_value: float = math.inf  # Set last scanned value to infinity

    def distance(self) -> float:
        """
        Returns the measured distance from the sonar if a delay of 100ms is reached; otherwise the function returns the last measured distance
        :return: float
        """
        if self.last_check < time.time_ns() + 100_000_000:  # Add execution delay of 100 ms
            self.prev_value = self.ultraSonic.value()
            self.last_check = time.time_ns()
        return self.prev_value

    def is_colliding(self) -> bool:
        """
        Returns a boolean indicating if a collision is detected a head. The collision range is set in the constants class
        :return: bool
        """
        return self.distance() < constants.COLLIDING_RANGE  # Colliding range
