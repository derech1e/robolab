import ev3dev.ev3 as ev3

class Driver(object):
    def __init__(self):
        self.ml = ev3.LargeMotor("outA")
        self.ml.reset()
        self.ml.stop_action = "brake"

        self.mr = ev3.LargeMotor("outD")
        self.mr.reset()
        self.mr.stop_action = "brake"

        
    def turn(self, deg):
        pass

    # input from -100 to 100
    def drive(self, vml, vmr):
        self.ml.duty_cycle_sp = vml
        self.ml.command = "run-direct"
        self.ml.duty_cycle_sp = vmr
        self.ml.command = "run-direct"
        pass

    def stop(self):
        self.ml.stop()
        self.mr.stop()
