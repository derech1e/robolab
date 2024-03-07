import ev3dev.ev3 as ev3


class SpeakerSensor:

    def __init__(self):
        self.speaker = ev3.Sound()

    def play_beep(self):
        self.speaker.beep()

    def play_tone(self, sound_range=[(200, 100, 100), (500, 200)]):
        self.speaker.tone(sound_range)

    def play_speak(self, message="Hello There!"):
        self.speaker.speak(message)
