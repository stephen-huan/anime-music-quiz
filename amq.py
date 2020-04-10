"""
serves as the API for the website
Note that for selenium to work, if the window is not headless, it must be focused.
TODO: host game, automatically load unseen songs into the database
"""

import time, json, sys, signal, os, subprocess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import fingerprint

URL = "https://animemusicquiz.com/"  # url of the website
LOGIN = "login.json"                 # contains the username and password
LEN = 5                              # seconds to record for
VERBOSE = True                       # whether to be verbose or not
HEADLESS, MUTED = True, False        # whether to run headless or muted
LOG = "mistakes.txt"                 # information about anime it missed

with open(LOGIN) as f:
    login = json.load(f)
    USER, PASS = login["username"], login["password"]

def handler(signum, frame):
    """ Handles keyboard interrupt globally so it always cleanly exits. """
    driver.quit()
    # sys.exit() gets caught by try ... catch, os._exit() doesn't work
    subprocess.run(["kill", str(os.getpid())])

signal.signal(signal.SIGINT, handler)

def find_by_text(driver: webdriver.Chrome, text: str):
    """ Finds an element by text. """
    return driver.find_elements_by_xpath(f"//*[contains(text(), '{text}')]")

def login() -> webdriver.Chrome:
    """ Logs in and returns a webdriver object. """
    chrome_options = webdriver.ChromeOptions()
    if HEADLESS:
        chrome_options.add_argument("--headless")
    if MUTED:
        chrome_options.add_argument("--mute-audio")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(URL)
    driver.find_element_by_id("loginUsername").send_keys(USER)
    driver.find_element_by_id("loginPassword").send_keys(PASS)
    driver.find_element_by_id("loginButton").click()
    time.sleep(1)

    btn = driver.find_elements_by_id("alreadyOnlineContinueButton")
    if len(btn) > 0:
        btn[0].click()

    return driver

def enter_game(driver: webdriver.Chrome, room_name: str, room: int, password: str=None) -> None:
    """ Enters a game from the home page. """
    driver.find_element_by_id("mpPlayButton").click()

    driver.find_element_by_id("rbSearchInput").send_keys(room_name)
    time.sleep(1)
    top = driver.find_element_by_id(f"rbRoom-{room}")
    top.find_element_by_class_name("rbrJoinButton").click()

    title = driver.find_elements_by_id("swal2-title")
    if len(title) > 0:
        driver.find_element_by_class_name("swal2-input").send_keys(password)
        driver.find_element_by_class_name("swal2-confirm").click()

    time.sleep(1)
    ready_up(driver)

def block_recording(driver: webdriver.Chrome) -> None:
    """ Blocks until it's time to start recording. """
    while True:
        try:
            t = driver.find_element_by_id("qpHiderText")
            txt = t.text.strip()
            # if it's showing a high number, start recording
            if txt in set(str(i) for i in range(15, 21)):
                break
            ready_up(driver)
        except: pass

def block_answer(driver: webdriver.Chrome) -> None:
    """ Blocks until the answer is revealed. """
    while True:
        try:
            t = driver.find_element_by_id("qpAnimeNameHider")
            if "hide" in t.get_attribute("class"):
                break
            vote_skip(driver)
        except: pass

def ready_up(driver: webdriver.Chrome) -> None:
    """ Clicks the ready button. """
    try:
        btn = driver.find_element_by_id("lbStartButton")
        if btn.text.strip() == "Ready" or btn.text.strip() == "Start":
            btn.click()
    except: pass

def vote_skip(driver: webdriver.Chrome) -> None:
    """ Who has time to listen to the entire song? """
    try:
        btn = driver.find_element_by_id("qpVoteSkip")
        if "toggled" not in btn.get_attribute("class").split():
            btn.click()
    except: pass

def get_anime(driver: webdriver.Chrome) -> tuple:
    """ Gets information about an anime. """
    try:
        name = driver.find_element_by_id("qpAnimeName").text.strip()
        link = driver.find_element_by_id("qpSongVideoLink").get_attribute("href").strip()
        typ = driver.find_element_by_id("qpSongType").text.split()
        op_ed = "op" if typ[0][0].lower() == "o" else "ed"
        num = int(typ[1])
        return link, name, op_ed, num
    except: return (None,)*4

def get_score(driver: webdriver.Chrome) -> int:
    """ Gets the bot's current score. """
    try:
        scoreboard = driver.find_element_by_id("qpScoreBoardEntryContainer")
        players = scoreboard.find_elements_by_class_name("qpScoreBoardEntry")
        for player in players:
            if USER in player.text:
                return int(player.text.split()[0])
        return 0
    except: return 0

def log_mistake(info: tuple) -> None:
    """ Logs the mistake information to a file. """
    with open(LOG, "a") as f:
        f.write("|".join(map(str, info)) + "\n")

def answer(driver: webdriver.Chrome, ans: str) -> None:
    """ Gives an answer. """
    box = driver.find_element_by_id("qpAnswerInput")
    box.send_keys(ans)
    box.send_keys(Keys.RETURN)

driver = login()

if __name__ == "__main__":
    enter_game(driver, input("Room name? "), int(input("Room number? ")), input("Room password? "))
    while True:
        try:
            block_recording(driver)
            before = get_score(driver)
            ans = fingerprint.find_song(LEN)
            answer(driver, ans)
            if VERBOSE: print(f"Predicting {ans}")
            block_answer(driver)
            # sometimes takes some time to load
            time.sleep(1)
            after = get_score(driver)
            # if the score is the same before and after answering a question, it got it wrong
            if VERBOSE: print("Mistake detected..." if before == after else "Got it right!")
            if before == after:
                log_mistake(get_anime(driver))
            vote_skip(driver)
        except Exception as e: print(e)
