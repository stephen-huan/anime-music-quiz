# maintains the song database
import argparse
import json
import os
import random
from pathlib import Path

import numpy as np

from amqlib import audio

PATH = Path("songs")  # where the songs are stored
DB = PATH / "sampled_down"  # cached reduced songs
INFO = PATH / "info.json"  # file storing metadata
ORIG = PATH / "original"  # untampered with song files
EXT = "mp3"  # extension for each song
EXT2 = "npy"  # alternative extension


def get_paths() -> list:
    """Returns the paths to each song."""
    return [path for path in PATH.rglob(f"*.{EXT}")]


def get_cached_paths() -> list:
    """Returns the list of songs that have already been preprocessed."""
    return [path for path in DB.rglob(f"*.{EXT2}")]


def load_db() -> dict:
    """Loads the json file."""
    if os.path.exists(INFO):
        with open(INFO) as f:
            return json.load(f)
    return {}


def save_db(data: dict) -> None:
    """Stores an updated version to the database."""
    with open(INFO, "w") as f:
        json.dump(data, f)


def gen_cache(force: bool = False) -> None:
    """Applies the preprocessing defined in audio to each song."""
    db = load_db()
    cached = [path.stem for path in get_cached_paths()]

    for path in get_paths():
        name = path.stem
        if name not in cached or force:
            song = audio.set_samplerate(path)
            vol, song = audio.preprocess(song)
            audio.save_file(DB / name, song)

            if name not in db:
                db[name] = {"vol": None, "anime": None}
            db[name]["vol"] = float(vol)

    save_db(db)


def prompt_user() -> None:
    """Asks the user from which anime a mp3 file comes from."""
    db = load_db()
    for name, info in db.items():
        if info["anime"] is None:
            info["anime"] = input(
                f"From which anime does the file {name} come from? "
            )

    save_db(db)


def update_db(force: bool = False) -> None:
    """Updates the database."""
    gen_cache(force)
    prompt_user()
    make_samplerate()


def make_samplerate() -> None:
    """Makes the sample rate of all the songs consistent."""
    for path in get_paths():
        sample_rate = audio.get_samplerate(path)
        if sample_rate != audio.ORIG:
            ORIG.mkdir(parents=True, exist_ok=True)
            dest = ORIG / path.stem / f".{EXT}"
            path.rename(dest)
            audio.samplerate(dest, path, audio.ORATE)


def random_song(verbose: bool = True) -> np.ndarray:
    """Returns a random song from the database for testing purposes."""
    mn, mx = -10, 10
    dB = (mx - mn) * np.random.random_sample() + mn
    song = random.choice(get_paths())
    if verbose:
        print(
            f"Picking a clip from {get_name(song)} at {'+' if dB >= 0 else ''}{round(dB, 2)}dB"
        )
    return 1 / 3 * audio.set_samplerate(song)
    # return audio.set_volume(audio.set_samplerate(song), dB)


def gen_test_case(length: int = 10, play: bool = False) -> np.ndarray:
    """Makes a test case by picking a random song and returning a clip from that song."""
    clip = audio.snippet(random_song(), length * audio.FS)
    audio.save_file("clip", clip)
    if play:
        audio.play(clip)
    return clip


def get_songs() -> list[tuple[Path, float, str]]:
    """Returns a list of (song path, volume, anime name) from the database."""
    db = load_db()
    songs = []
    for path in get_cached_paths():
        name = path.stem
        songs.append((path, db[name]["vol"], db[name]["anime"]))
    return songs


db = load_db()
if (
    len(db) == 0
    or len(db) < len(get_paths())
    or any(info["anime"] is None for info in db.values())
):
    DB.mkdir(parents=True, exist_ok=True)
    update_db()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maintains a song database.")
    parser.add_argument("-v", "--version", action="version", version="AMQ 1.0")

    subparsers = parser.add_subparsers(title="commands")
    update = subparsers.add_parser("update", help="updates the database")
    update.add_argument(
        "-f",
        "--force",
        help="whether to rebuilt the cache.",
        action="store_true",
    )
    update.set_defaults(func=lambda args: update_db(args.force))
    clip = subparsers.add_parser("clip", help="generates a test case")
    clip.add_argument(
        "-l", "--length", type=int, help="length of the clip", default=10
    )
    clip.add_argument(
        "-p",
        "--play",
        help="whether play the generated clip.",
        action="store_true",
    )
    clip.set_defaults(func=lambda args: gen_test_case(args.length, args.play))
    play = subparsers.add_parser("play", help="plays the test case")
    play.set_defaults(func=lambda _: audio.play(audio.load_file("clip.npy")))
    size = subparsers.add_parser(
        "size", help="prints the size of the database"
    )
    size.set_defaults(
        func=lambda _: print(f"{len(db)} songs in the database.")
    )

    args = parser.parse_args()
    if "func" in args:
        args.func(args)
