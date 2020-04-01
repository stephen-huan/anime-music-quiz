"""
set the IN variable to a loopback device to record current system sound
(get the ids of each thing by print(sd.query_devices()) or python -m sounddevice
NOTE: on macOS, most applications are BANNED from recording, including Python
Here's what I did: get audacity, use the open command to launch it in terminal
that allows you to add terminal to the list of apps allowed to access the microphone
"""
import time
import sounddevice as sd
import numpy as np
from audio2numpy import open_audio

FS = int(48*1000)   # 48 kHz sampling rate
IN = 2              # should be soundflower 2ch on macOS
BUCKET = (1 << 4)   # must be a divisor of FS, factor of size reduction

assert FS % BUCKET == 0

def save_file(fname: str, data: np.array):
    """ Saves a numpy array to a file. """
    np.save(fname, data)

def load_file(fname: str) -> np.array:
    """ Loads a numpy array from a file. """
    return np.load(fname)

def load_mp3(fname: str) -> np.array:
    """ Loads a mp3 file as a numpy array. """
    data, sampling_rate = open_audio(fname)
    assert sampling_rate == FS
    return data

def avg_channels(data: np.array) -> np.array:
    """ Averages all the channels together into one mono channel. """
    chs = len(data[0])
    mono = np.zeros(len(data))
    for ch in range(chs):
        mono += data[:, ch]
    return mono/chs

def scale(data: np.array) -> np.array:
    """ Turns a variance of [-1, 1], floating point
    into [0, 2^16], integer for mathematical reasons. """
    return ((1 << 16)*(data + 1)).astype(int)

def unscale(data: np.array) -> np.array:
    return data/(1 << 16) - 1

def compress(data: np.array) -> np.array:
    """ Compresses the array down using a heuristical process. """
    l = []
    for i in range(0, len(data), BUCKET):
        l.append(np.sum(data[i:i + BUCKET])/BUCKET)
    return np.array(l)

def uncompress(data: np.array) -> np.array:
    l = []
    for num in data:
        for i in range(BUCKET):
            l.append(num)
    return np.array(l)

def play_song(data: np.array) -> None:
    """ Plays a song to the default speaker. """
    sd.play(data, FS)
    sd.wait()

if __name__ == "__main__":
    data = load_mp3("songs/bakemonogatari_ed1.mp3")
    data = avg_channels(data)
    data = compress(data)
    print(len(data))
    # data = scale(data)
    # data = unscale(data)

    play_song(uncompress(data))
    exit()

    print("recording")
    data = sd.rec(int(5*FS), samplerate=FS, channels=1, device=IN)
    sd.wait()
    save_file(data)
