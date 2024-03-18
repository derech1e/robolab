import ev3dev.ev3 as ev3


class SpeakerSensor:
    """
    This class is used to control the speaker sensor of the ev3 brick
    """

    def __init__(self):
        """
        Initializes the speaker sensor
        """
        self.speaker = ev3.Sound()

    def play_beep(self) -> None:
        """
        Plays a beep on the brick
        :return: void
        """
        self.speaker.beep()

    def play_tone(self, sound_range=[(200, 100, 100), (500, 200)]) -> None:
        """
        Plays a tone in a given sound range
        :param sound_range: list[tuple[int, (...int)]]
        :return: void
        """
        self.speaker.tone(sound_range)

    def play_speak(self, message="Hello There!") -> None:
        """
        Read out a message
        :param message: String
        :return: void
        """
        self.speaker.speak(message)
