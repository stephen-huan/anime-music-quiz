# identifies songs with a fingerprint method
import json, time, argparse, os
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer

PATH = "songs"               # where the songs are stored
INFO = PATH + "/info.json"   # file storing metadata
EXT = ".mp3"                 # extension for each song

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

def prompt_user() -> None:
    """ Asks the user from which anime a mp3 file comes from. """
    db = load_db()
    for name, info in db.items():
        if info["anime"] is None:
            info["anime"] = input(f"From which anime does the file {name} come from? ")

    save_db(db)

def update() -> None:
    """ Updates the database. """
    djv.fingerprint_directory(PATH, [EXT], 1)
    prompt_user()
    # print(djv.db.get_num_fingerprints())

def _find_song(length: int=10, verbose: bool=True):
    """ Records a clip and finds where that clip comes from. """
    start = time.time()
    song = djv.recognize(MicrophoneRecognizer, seconds=length)
    if verbose:
        print(f"{round((time.time() - start) - length, 2)} seconds to find an answer")
    # no matches
    if len(song[0]) == 0:
        print("Found no matches. Are you sure the loopback device is working?")
        # it's Renai Circulation!
        return f"Bakemonogatari-OP4"
    return song[0][0]["song_name"].decode("utf-8")

def find_song(length: int=10, verbose: bool=True):
    """ Returns the anime name of the clip. """
    return db[_find_song(length, verbose)]["anime"]

config = json.load(open("config.json"))
djv = Dejavu(config)
db = load_db()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maintains a song database.")
    parser.add_argument("-v", "--version", action="version", version="AMQ 1.0")
    subparsers = parser.add_subparsers(title="commands")
    up = subparsers.add_parser("update", help="updates the database")
    up.set_defaults(func=lambda args: update())
    find = subparsers.add_parser("find", help="recognizes a clip from the microphone")
    find.set_defaults(func=lambda args: print(find_song()))

    args = parser.parse_args()
    if "func" in args:
        args.func(args)

    # song = djv.recognize(FileRecognizer, "songs/MonogatariSecondSeries_op4.mp3")
    # print(song)

    # start = time.time()
    # song = find_song()
    # print(song)
    # print((time.time() - start) - 10)
