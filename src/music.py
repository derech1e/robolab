duckys = [(523, 100, 100), (587, 100, 100), (659.26, 100, 100), (698, 100, 100), (784, 200, 200), (784, 200, 200),
          (880, 100, 100), (880, 100, 100), (880, 100, 100), (880, 100, 100), (784, 400, 400), (880, 100, 100),
          (880, 100, 100), (880, 100, 100), (880, 100, 100), (784, 400, 400), (698, 100, 100), (698, 100, 100),
          (698, 100, 100), (698, 100, 100), (659.26, 200, 200), (659.26, 200, 200), (784, 100, 100), (784, 100, 100),
          (784, 100, 100), (784, 100, 100), (523, 800, 800)]


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
