def fft(a: list, b: list) -> list:
    """Multiplies two polynomials given by
    (a[0] + a[1]x + a[2]x^2 + ...)(b[0] + b[1]x + b[2]x^2 + ...)."""
    # TODO: replace with fft
    p = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            p[i + j] += a[i] * b[j]
    return p


def brute_force(a: list, b: list) -> int:
    # for i in range(len(b) - len(a) + 1):
    #     print(sum((a[j] - b[j + i])**2 for j in range(len(a))), sum(abs(a[j] - b[j + i]) for j in range(len(a))))
    return min(
        range(len(b) - len(a) + 1),
        key=lambda i: sum((a[j] - b[j + i]) ** 2 for j in range(len(a))),
    )


import wave

### AUDIO
##### PYAUDIO
import pyaudio

IN = 2
OUT = None


def play_audio(fname: str):
    # Set chunk size of 1024 samples per data frame
    chunk = 1024

    # Open the sound file
    f = wave.open(fname, "rb")

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(
        format=p.get_format_from_width(f.getsampwidth()),
        channels=f.getnchannels(),
        rate=f.getframerate(),
        output=True,
    )

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while data != "":
        stream.write(data)
        data = wf.readframes(chunk)

    # Close and terminate the stream
    stream.close()
    p.terminate()


def record_audio():
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt32  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 3
    filename = "output.wav"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print("Recording")

    stream = p.open(
        format=sample_format,
        channels=channels,
        rate=fs,
        frames_per_buffer=chunk,
        input_device_index=IN,
        input=True,
    )

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print("Finished recording")

    # Save the recorded data as a WAV file
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b"".join(frames))
    wf.close()


record_audio()

##### PLAYSOUND

from playsound import playsound

SONG = "songs/bakemonogatari_ed1.mp3"
playsound(SONG)

##### SOUNDCARD
import numpy as np
import soundcard as sc

FS = int(44.1 * 1000)  # 48 kHz sampling rate

print(sc.all_microphones())
mic = sc.default_microphone()
# mic = sc.get_microphone("Soundflower (64ch)")
speaker = sc.default_speaker()

print("recording")
data = mic.record(samplerate=FS, numframes=FS)
print("playing back")
# print(list(data))
speaker.play(data, samplerate=FS)

default_mic = sc.default_microphone()
with default_mic.recorder(48000, channels=[0]) as mic:
    data = mic.record(1024)
    print(data)

##### SOUNDDEVICE
import sounddevice as sd

IN = 4
OUT = 5

print(sd.query_devices())
print("recording")
data = sd.rec(int(5 * FS), samplerate=FS, channels=1, device=IN)
sd.wait()
print("playing back")
print(data)
sd.play(data, FS, device=OUT)
