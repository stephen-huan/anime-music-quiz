# maintains the song database
import subprocess, glob, json, os, argparse, random
import numpy as np
import audio

PATH = "songs"               # where the songs are stored
DB = PATH + "/sampled_down"  # cached reduced songs
EXT = ".mp3"                 # extension for each song
INFO = PATH + "/info.json"   # file storing metadata
EXT2 = ".npy"                # alternative extension
ORIG = PATH + "/original"    # untampered with song files

def get_paths() -> list:
    """ Returns the paths to each song. """
    return [path for path in glob.glob(f"{PATH}/*{EXT}")]

def get_cached_paths() -> list:
    """ Returns the list of songs that have already been preprocessed. """
    return [path for path in glob.glob(f"{DB}/*{EXT2}")]

def get_name(path: str) -> str:
    """ Returns the name from a path. """
    return path.split("/")[-1].split(".")[0]

def load_db() -> dict:
    """ Loads the json file. """
    if os.path.exists(INFO):
        with open(INFO) as f:
            return json.load(f)
    return {}

def save_db(data: dict) -> None:
    """ Stores an updated version to the database. """
    with open(INFO, "w") as f:
        json.dump(data, f)

def gen_cache(force: bool=False) -> None:
    """ Applies the preprocessing defined in audio to each song. """
    db = load_db()
    cached = [get_name(path) for path in get_cached_paths()]

    for path in get_paths():
        name = get_name(path)
        if name not in cached or force:
            song = audio.set_samplerate(path)
            vol, song = audio.preprocess(song)
            audio.save_file(f"{DB}/{name}", song)

            if name not in db:
                db[name] = {"vol": None, "anime": None}
            db[name]["vol"] = float(vol)

    save_db(db)

def prompt_user() -> None:
    """ Asks the user from which anime a mp3 file comes from. """
    db = load_db()
    for name, info in db.items():
        if info["anime"] is None:
            info["anime"] = input(f"From which anime does the file {name} come from? ")

    save_db(db)

def update_db(force: bool=False) -> None:
    """ Updates the database. """
    gen_cache(force)
    prompt_user()
    make_samplerate()

def make_samplerate() -> None:
    """ Makes the sample rate of all the songs consistent. """
    for path in get_paths():
        sample_rate = audio.get_samplerate(path)
        if sample_rate != audio.ORIG:
            if not os.path.exists(ORIG):
                os.mkdir(ORIG)
            dest = f"{ORIG}/{get_name(path)}{EXT}"
            os.rename(path, dest)
            audio.samplerate(dest, path, audio.ORATE)

def random_song(verbose: bool=True) -> np.array:
    """ Returns a random song from the database for testing purposes. """
    mn, mx = -10, 10
    dB = (mx - mn)*np.random.random_sample() + mn
    song = random.choice(get_paths())
    if verbose:
        print(f"Picking a clip from {get_name(song)} at {'+' if dB >= 0 else ''}{round(dB, 2)}dB")
    return audio.set_volume(audio.set_samplerate(song), dB)

def gen_test_case(length: int=10, play: bool=False) -> np.array:
    """ Makes a test case by picking a random song and returning a clip from that song. """
    clip = audio.snippet(random_song(), length*audio.FS)
    audio.save_file("clip", clip)
    if play:
        audio.play(clip)
    return clip

def get_songs() -> list:
    """ Returns a list of (song path, volume, anime name) tuples from the database. """
    db = load_db()
    songs = []
    for path in get_cached_paths():
        name = get_name(path)
        songs.append((path, db[name]["vol"], db[name]["anime"]))
    return songs

db = load_db()
if len(db) == 0 or len(db) < len(get_paths()) or any(info["anime"] is None for info in db.values()):
    update_db()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maintains a song database.")
    parser.add_argument("-v", "--version", action="version", version="AMQ 1.0")

    subparsers = parser.add_subparsers(title="commands")
    update = subparsers.add_parser("update", help="updates the database")
    update.add_argument("-f", "--force", help="whether to rebuilt the cache.", action="store_true")
    update.set_defaults(func=lambda args: update_db(args.force))
    clip = subparsers.add_parser("clip", help="generates a test case")
    clip.add_argument("-l", "--length", type=int, help="length of the clip", default=10)
    clip.add_argument("-p", "--play", help="whether play the generated clip.", action="store_true")
    clip.set_defaults(func=lambda args: gen_test_case(args.length, args.play))
    play = subparsers.add_parser("play", help="plays the test case")
    play.set_defaults(func=lambda args: audio.play(audio.load_file("clip.npy")))
    size = subparsers.add_parser("size", help="prints the size of the database")
    size.set_defaults(func=lambda args: print(f"{len(db)} songs in the database."))

    args = parser.parse_args()
    if "func" in args:
        args.func(args)
