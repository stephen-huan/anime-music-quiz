"""
set the IN variable to a loopback device to record current system sound
(get the ids by print(sd.query_devices()) or python -m sounddevice
NOTE: on macOS, most applications are BANNED from recording, including Python.
Here's what I did: get audacity, use the open command to launch it in terminal.
That allows you to add terminal to the list
of apps allowed to access the microphone.

on a Raspberry Pi:
arecord --channels=2 --duration=10 --device=hw:0,1 --format=dat --vumeter=stereo temp.wav
time aplay bakemonogatari_ed1.wav

keeping the volume lower seems to make arecord more consistent -
I suspect it can overflow on 100%, so I keep it at 85%.
"""

import json
import os
import subprocess
import sys

import numpy as np
import sounddevice as sd
from audio2numpy import open_audio
from pydub import AudioSegment
from pydub.utils import mediainfo
from scipy.io.wavfile import write

IN = json.load(open("params.json"))["IN"]  # should be soundflower 2ch on macOS
ORIG = int(48 * 1000)  # default 48 kHz sampling rate
ORATE = "48k"  # original rate, passed to ffmpeg
FS = int(8 * 1000)  # post-processed after ffmpeg down scaling
RATE = "8k"  # new rate, passed to ffmpeg
BUCKET = 1 << 5  # must be a divisor of FS, factor of size reduction
# assert FS % BUCKET == 0
MU = (1 << 8) - 1  # number of bits per number (usually 16 for mp3)
TEMP = "temp.mp3"  # temporary file path


def save_file(fname: str, data: np.ndarray):
    """Saves a numpy array to a file."""
    np.save(fname, data)


def load_file(fname: str) -> np.ndarray:
    """Loads a numpy array from a file."""
    return np.load(fname)


def load_mp3(fname: str) -> np.ndarray:
    """Loads a mp3 file as a numpy array."""
    data, sampling_rate = open_audio(fname)
    assert sampling_rate == FS or sampling_rate == ORIG
    return data


def save_mp3(fname: str, data: np.ndarray, rate: int = FS) -> None:
    """Saves data into the WAV format."""
    write(fname, rate, data)


def samplerate(fname: str, out: str = TEMP, rate: str = RATE) -> None:
    """Uses ffmpeg to set the sample rate of a file."""
    subprocess.call(
        ["ffmpeg", "-loglevel", "quiet", "-y", "-i", fname, "-ar", rate, out]
    )


def get_samplerate(fname: str) -> int:
    """Returns the sample rate of a file."""
    return int(mediainfo(fname)["sample_rate"])


def set_samplerate(fname: str, rate: str = RATE) -> np.ndarray:
    """Converts an array recorded in one sample rate to one in another."""
    samplerate(fname, TEMP, rate)
    data = load_mp3(TEMP)
    os.remove(TEMP)
    return data


def set_volume(data: np.ndarray, vol: int) -> np.ndarray:
    """Changes the volume of a song.
    TODO: make it not stupid."""
    save_mp3("temp.wav", data)
    song = AudioSegment.from_wav("temp.wav")
    os.remove("temp.wav")
    song += vol
    song.export(TEMP)
    data = load_mp3(TEMP)
    os.remove(TEMP)
    return data


def rge(data: np.ndarray) -> float:
    """Finds the range of the original data for volume scaling purposes."""
    return np.max(data) - np.min(data)


def avg_channels(data: np.ndarray) -> np.ndarray:
    """Averages all the channels together into one mono channel."""
    # already has only one channel
    if data.ndim == 1:
        return data

    chs = len(data[0])
    mono = np.zeros(len(data))
    for ch in range(chs):
        mono += data[:, ch]
    return mono / chs


def scale(data: np.ndarray) -> np.ndarray:
    """Turns a range of [-1, 1], floating point
    into [0, BITS), integer for mathematical reasons.
    See: https://en.wikipedia.org/wiki/%CE%9C-law_algorithm"""
    f = np.sign(data) * np.log(1 + MU * np.abs(data)) / np.log(1 + MU)
    return ((MU >> 1) * (f + 1)).astype(int)


def unscale(data: np.ndarray) -> np.ndarray:
    """Reverses scale."""
    data = data / (MU >> 1) - 1
    return np.sign(data) * (1 / MU) * (np.power(1 + MU, np.abs(data)) - 1)


def compress(data: np.ndarray) -> np.ndarray:
    """Compresses the array down using a heuristical process.
    DEPRECIATED: use `ffmpeg -y -i song.mp3 -ar 8000 out.mp3`.
    """
    new_data = []
    for i in range(0, len(data), BUCKET):
        new_data.append(np.sum(data[i : i + BUCKET]) / BUCKET)
    return np.array(new_data)


def uncompress(data: np.ndarray) -> np.ndarray:
    """Uncompresses the array by reversing compress.
    DEPRECIATED: just set the sample rate in play.
    """
    new_data = []
    for num in data:
        for _ in range(BUCKET):
            new_data.append(num)
    return np.array(new_data)


def preprocess(data: np.ndarray) -> tuple:
    """Prepares an array for audio analysis."""
    return rge(data), scale(compress(avg_channels(data)))


def snippet(data: np.ndarray, length: int = 10 * FS) -> np.ndarray:
    """Returns a random snippet of the array for use in debugging."""
    i = np.random.randint(len(data) - length)
    return data[i : i + length]


def play(data: np.ndarray, rate: int = FS) -> None:
    """Plays a song to the default speaker."""
    sd.play(data, rate)
    sd.wait()


def record(length: int, rate: int = FS) -> np.ndarray:
    """Records a segment from the microphone (does not block)."""
    return sd.rec(int(length * rate), samplerate=rate, channels=1, device=IN)


def rpi_record(length: int, rate: int = FS) -> np.ndarray:
    """Records a segment from the microphone (blocks)."""
    rate  # pyright: ignore
    subprocess.call(
        [
            "arecord",
            "--channels=2",
            f"--duration={length}",
            "--device=hw:0,1",
            "--format=dat",
            "--vumeter=stereo",
            "temp.wav",
        ]
    )
    return set_samplerate("temp.wav")


# if on linux, switch record method
if sys.platform.startswith("linux"):
    record = rpi_record

if __name__ == "__main__":
    # data = set_samplerate("songs/bakemonogatari_ed1.mp3")

    # data = avg_channels(data)
    # # print(len(data))
    # data = scale(data)
    # data = unscale(data)
    # data = compress(data)
    # data = uncompress(data)

    # save_mp3("test.wav", data)
    # play(data)
    # exit()

    print("recording")
    data = record(5)
    sd.wait()
    save_file("temp", data)

    data = load_file("temp.npy")
    print(data, len(data))
    play(data)
