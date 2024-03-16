duckys = [(523, 100, 100), (587, 100, 100), (659.26, 100, 100), (698, 100, 100), (784, 200, 200), (784, 200, 200),
          (880, 100, 100), (880, 100, 100), (880, 100, 100), (880, 100, 100), (784, 400, 400), (880, 100, 100),
          (880, 100, 100), (880, 100, 100), (880, 100, 100), (784, 400, 400), (698, 100, 100), (698, 100, 100),
          (698, 100, 100), (698, 100, 100), (659.26, 200, 200), (659.26, 200, 200), (784, 100, 100), (784, 100, 100),
          (784, 100, 100), (784, 100, 100), (523, 800, 800)]

imperial_march = [(392, 350, 100), (392, 350, 100), (392, 350, 100), (311.1, 250, 100), (466.2, 25, 100),
                  (392, 350, 100), (311.1, 250, 100), (466.2, 25, 100), (392, 700, 100), (587.32, 350, 100),
                  (587.32, 350, 100), (587.32, 350, 100), (622.26, 250, 100), (466.2, 25, 100), (369.99, 350, 100),
                  (311.1, 250, 100), (466.2, 25, 100), (392, 700, 100), (784, 350, 100), (392, 250, 100),
                  (392, 25, 100), (784, 350, 100), (739.98, 250, 100), (698.46, 25, 100), (659.26, 25, 100),
                  (622.26, 25, 100), (659.26, 50, 400), (415.3, 25, 200), (554.36, 350, 100), (523.25, 250, 100),
                  (493.88, 25, 100), (466.16, 25, 100), (440, 25, 100), (466.16, 50, 400), (311.13, 25, 200),
                  (369.99, 350, 100), (311.13, 250, 100), (392, 25, 100), (466.16, 350, 100), (392, 250, 100),
                  (466.16, 25, 100), (587.32, 700, 100), (784, 350, 100), (392, 250, 100), (392, 25, 100),
                  (784, 350, 100), (739.98, 250, 100), (698.46, 25, 100), (659.26, 25, 100), (622.26, 25, 100),
                  (659.26, 50, 400), (415.3, 25, 200), (554.36, 350, 100), (523.25, 250, 100), (493.88, 25, 100),
                  (466.16, 25, 100), (440, 25, 100), (466.16, 50, 400), (311.13, 25, 200), (392, 350, 100),
                  (311.13, 250, 100), (466.16, 25, 100), (392.00, 300, 150), (311.13, 250, 100), (466.16, 25, 100),
                  (392, 700)]

def generate():
    l = 100
    notes = [523, 587, 659.26, 698, 784, 784, 880, 880, 880,
             880, 784, 880, 880, 880,
             880, 784, 698, 698, 698, 698, 659.26, 659.26, 784, 784, 784, 784, 523]
    durations = [l, l, l, l, 2 * l, 2 * l, l, l, l, l, 4 * l, l, l, l, l, 4 * l, l, l, l, l, 2 * l, 2 * l, l, l, l, l,
                 8 * l]

    mel = []

    for i in range(len(notes)):
        mel.append((notes[i], durations[i], durations[i]))

    print(mel)
