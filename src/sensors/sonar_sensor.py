import math
import time
import constants

import ev3dev.ev3 as ev3


class SonarSensor:

    def __init__(self):
        self.ultraSonic = ev3.UltrasonicSensor()
        self.ultraSonic.mode = 'US-DIST-CM'  # Continuous measurement in centimeters (for inch use US-DIST-IN)
        self.last_check = -1
        self.prev_value = math.inf
        # ultraSonic.mode = 'US-SI-CM'  # Single measurement in centimeters (for inch use US-SI-IN)

    def distance(self):
        if self.last_check < time.time_ns() + 100_000_000:  # Add execution delay of 100 ms
            self.prev_value = self.ultraSonic.value()
            self.last_check = time.time_ns()
        return self.prev_value

    def is_colliding(self):
        return self.distance() < constants.COLLIDING_RANGE  # Colliding range
