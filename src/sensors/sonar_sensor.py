import ev3dev.ev3 as ev3


class SonarSensor:

    def __init__(self):
        self.ultraSonic = ev3.UltrasonicSensor()
        self.ultraSonic.mode = 'US-DIST-CM'  # Continuous measurement in centimeters (for inch use US-DIST-IN)
        # ultraSonic.mode = 'US-SI-CM'  # Single measurement in centimeters (for inch use US-SI-IN)

    def distance(self):
        return self.ultraSonic.value()

    def is_colliding(self):
        return self.distance() < 4  # Colliding range
