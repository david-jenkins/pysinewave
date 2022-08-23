from pysinewave import BeatWave
import time

def play_tone():
    # the second argument of BeatWave is the beat frequency, others are the same as SineWave

    sw = BeatWave(12,1,20)

    sw.play()

    time.sleep(3)

    # A beat frequency of zero gives a continuous sine wave the same as SineWave
    sw.set_beat_frequency(0)

    time.sleep(1)

    # the frequency of the 2 beating tones is calculated such that the correct pitch is played
    sw.set_pitch(5)

    time.sleep(1)

    sw.set_pitch(10)

    time.sleep(2)

    sw.set_pitch(-7)

    time.sleep(1)

    sw.set_beat_frequency(10)

    time.sleep(2)

    sw.set_pitch(5)

    time.sleep(2)

    sw.stop()

if __name__ == "__main__":
    play_tone()