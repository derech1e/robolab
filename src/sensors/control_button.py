import time

import ev3dev.ev3 as ev3


class ControlButton:
    """
    Class to manage the button interface of the brick
    """

    def __init__(self):
        self.pressed = False
        self.button = ev3.Button()
        self.button.on_enter = self.on_enter

    def on_enter(self, state) -> None:
        """
        Sets internal pressed variable to true if button is pressed
    :   return: Void
        """
        self.pressed = True

    def wait_for_input(self) -> None:
        """
        Function that loops until button is pressed
        :return: Void
        """
        while not self.pressed:
            # calls the bricks internal routine to check the buttons for input
            self.button.process()
            time.sleep(0.250)
        self.pressed = False
