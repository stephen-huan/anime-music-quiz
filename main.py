import time

import numpy as np

import db
from amqlib import audio, solver


def offset_time(t: int) -> float:
    """Converts an array position to a time in seconds."""
    return round(audio.BUCKET * t / audio.FS, 1)


def test_against(
    vol1: float, data: np.ndarray, vol2: float, song: np.ndarray
) -> tuple:
    """Tests a clip against a song."""
    (vol1, vol2)  # pyright: ignore
    # f = solver.loss_func(data, song)
    # for k in range(20):
    #     print(k/10, f(k/10))
    # print(solver.one_d_min(f, 0, 2), vol1, vol2)
    # return solver.solve((solver.one_d_min(f, 0, vol2/vol1)*data).astype(int), song)
    return solver.solve(data, song)  # type: ignore


def find_song(vol1: float, data: np.ndarray, verbose: bool = False) -> str:
    """Finds the name of the anime a clip occurs from."""
    start = time.time()
    songs = db.get_songs()
    pos, best, ans, best_song = 0, float("inf"), "", ""
    for path, vol2, anime in sorted(songs):
        song = audio.load_file(path)
        p, l2 = test_against(vol1, data, vol2, song)
        if l2 < best:
            pos, best, ans, best_song = p, l2, anime, path.stem
        if verbose:
            print(
                f"{path.stem:<30}: {l2:<10} loss, occurs at {offset_time(p):<5} seconds in"
            )
    if verbose:
        print("-" * 10)
        print(
            f"Final answer: {ans}, song is {best_song} and clip occurs {offset_time(pos)} seconds in"
        )
        sec = round(time.time() - start, 2)
        print(
            f"{len(songs)} songs in {sec} seconds = {round(len(songs)/sec, 2)} songs per second"
        )
    return ans


if __name__ == "__main__":
    raw_clip = audio.load_file("clip.npy")
    vol1, clip = audio.preprocess(raw_clip)

    anime = find_song(vol1, clip, True)
    # print(anime)

    # raw_clip, raw_song = audio.load_file("clip.npy"), audio.load_file(
    #     "songs/sampled_down/bakemonogatari_ed1.npy"
    # )
    # vol1, clip = audio.preprocess(raw_clip)
    # vol2, song = vol1, raw_song
    # # vol2, song = audio.preprocess(raw_song)
    # pos, l2 = test_against(vol1, clip, vol2, song)
    #
    # print(f"Clip occurs about {audio.offset_time(pos)} seconds into the song")
    # print("Playing clip:")
    # audio.play(raw_clip)
    # print("Playing from the estimated position in the original song:")
    # audio.play(raw_song[pos:pos + len(raw_clip)])
