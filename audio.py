"""
set the IN variable to a loopback device to record current system sound
(get the ids of each thing by print(sd.query_devices()) or python -m sounddevice
NOTE: on macOS, most applications are BANNED from recording, including Python
Here's what I did: get audacity, use the open command to launch it in terminal
that allows you to add terminal to the list of apps allowed to access the microphone
"""
import subprocess
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from audio2numpy import open_audio

# FS = int(48*1000)   # 48 kHz sampling rate
FS = int(8*1000)      # post-processed after ffmpeg down scaling
IN = 2                # should be soundflower 2ch on macOS
BUCKET = 1 << 5       # must be a divisor of FS, factor of size reduction
# assert FS % BUCKET == 0
RATE = "8k"           # new rate, passed to ffmpeg
BITS = 1 << 8         # number of bits per number (usually 16 for mp3)

def save_file(fname: str, data: np.array):
    """ Saves a numpy array to a file. """
    np.save(fname, data)

def load_file(fname: str) -> np.array:
    """ Loads a numpy array from a file. """
    return np.load(fname + ".npy")

def load_mp3(fname: str) -> np.array:
    """ Loads a mp3 file as a numpy array. """
    data, sampling_rate = open_audio(fname)
    # assert sampling_rate == FS
    return data

def save_mp3(fname: str, data: np.array, rate: int=FS) -> None:
    """ Saves data into the WAV format. """
    write(fname, rate, data)

def set_samplerate(data: np.array, original: int=FS, rate: int=48000):
    """ Converts an array recorded in one sample rate to one in another. """
    # subprocess.call(["ffmpeg", "-y", "-i", "songs/bakemonogatari_ed1.mp3", "-ar", "8k", "song.mp3"])

def rge(data: np.array) -> float:
    """ Finds the range of the original data for volume scaling purposes. """
    return np.max(data) - np.min(data)

def avg_channels(data: np.array) -> np.array:
    """ Averages all the channels together into one mono channel. """
    # already has only one channel
    if isinstance(data.shape, int):
        return data

    chs = len(data[0])
    mono = np.zeros(len(data))
    for ch in range(chs):
        mono += data[:, ch]
    return mono/chs

def scale(data: np.array) -> np.array:
    """ Turns a variance of [-1, 1], floating point
    into [0, BITS], integer for mathematical reasons. """
    return ((BITS >> 1)*(data + 1)).astype(int)

def unscale(data: np.array) -> np.array:
    """ Reverses scale. """
    return data/(BITS >> 1) - 1

def compress(data: np.array) -> np.array:
    """ Compresses the array down using a heuristical process.
    DEPRECIATED: use `ffmpeg -y -i song.mp3 -ar 8000 out.mp3`.
    """
    l = []
    for i in range(0, len(data), BUCKET):
        l.append(np.sum(data[i:i + BUCKET])/BUCKET)
    return np.array(l)

def uncompress(data: np.array) -> np.array:
    """ Uncompresses the array by reversing compress.
    DEPRECIATED: just set the sample rate in play_song.
    """
    l = []
    for num in data:
        for i in range(BUCKET):
            l.append(num)
    return np.array(l)

def preprocess(data: np.array) -> tuple:
    """ Prepares an array for audio analysis. """
    return rge(data), scale(compress(avg_channels(data)))

def snippet(data: np.array, length: int=10*FS) -> np.array:
    """ Returns a random snippet of the array for use in debugging. """
    i = np.random.randint(len(data) - length)
    print(i/FS)
    return data[i: i + length]

def play_song(data: np.array, rate: int=FS) -> None:
    """ Plays a song to the default speaker. """
    sd.play(data, rate)
    sd.wait()

def record(length: int) -> np.array:
    """ Records a segment from the microphone (does not block). """
    return sd.rec(int(length*FS), samplerate=FS, channels=1, device=IN)

if __name__ == "__main__":
    data = load_mp3("songs/sampled_down/bakemonogatari_ed1.mp3")

    snip = snippet(data)
    # play_song(snip)
    save_file("clip", snip)
    exit()

    data = avg_channels(data)
    # print(len(data))
    data = scale(data)
    data = unscale(data)
    # data = compress(data)
    # data = uncompress(data)

    # save_mp3("test.wav", data)
    # play_song(data)
    exit()

    print("recording")
    data = record(5)
    sd.wait()
    save_file("temp", data)

    print(data)
    data = load_file("temp")
    play_song(data)
