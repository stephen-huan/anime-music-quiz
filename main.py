import audio
import solver
import numpy as np

def offset_time(t: int) -> float:
    """ Converts an array position to a time in seconds. """
    return round(audio.BUCKET*t/audio.FS, 1)

def test_against(vol1: float, data: np.array, vol2: float, song: np.array) -> tuple:
    """ Tests a clip against a song. """
    # scales the clip to the proper volume
    datap = ((vol2/vol1)*data).astype(int)
    return solver.solve(datap, song)

if __name__ == "__main__":
    raw_clip, raw_song = audio.load_file("clip"), audio.load_mp3("songs/sampled_down/bakemonogatari_ed1.mp3")
    vol1, clip = audio.preprocess(raw_clip)
    vol2, song = audio.preprocess(raw_song)
    pos, l2 = test_against(vol1, clip, vol2, song)

    print(f"Clip occurs about {offset_time(pos)} seconds into the song")
    # print("Playing clip:")
    # audio.play_song(raw_clip)
    # print("Playing from the estimated position in the original song:")
    # audio.play_song(raw_song[pos:pos + len(raw_clip)])
