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
        self.ml.speed_sp = vml
        self.ml.command = "run-forever"
        self.mr.speed_sp = vmr
        self.mr.command = "run-forever"
        pass

    def stop(self):
        self.ml.stop()
        self.mr.stop()
