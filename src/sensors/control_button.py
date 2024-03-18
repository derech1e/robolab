import time

import ev3dev.ev3 as ev3


class ControlButton:

    def __init__(self):
        self.pressed = False
        self.button = ev3.Button()
        self.button.on_enter = self.on_enter

    def on_enter(self, state):
        self.pressed = True

    def wait_for_input(self):
        while not self.pressed:
            self.button.process()
            time.sleep(0.250)
        self.pressed = False
