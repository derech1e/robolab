import time

import ev3dev.ev3 as ev3


class ControlButton:

    def __init__(self):
        self.button = ev3.Button()
        self.on_enter = self.on_enter

    def on_enter(self, state) -> bool:
        return state

    def wait_for_input(self):
        while True:
            self.button.process()
            time.sleep(0.250)
