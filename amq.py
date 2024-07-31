"""
serves as the API for the website
Note that for selenium to work, if the window is not headless, it must be focused.
TODO: host game, automatically load unseen songs into the database
"""

import getpass
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import main
from amqlib import audio

URL = "https://animemusicquiz.com/"  # url of the website
LOGIN = "login.json"  # contains the username and password
LEN = 10  # seconds to record for
VERBOSE = True  # whether to be verbose or not
HEADLESS, MUTED = True, False  # whether to run headless or muted

# load login information from file
if os.path.exists(LOGIN):
    with open(LOGIN) as f:
        login_info = json.load(f)
        USER, PASS = login_info["username"], login_info["password"]
# prompt for information
else:
    USER, PASS = input("Username: "), getpass.getpass()


def find_by_text(driver: webdriver.Chrome, text: str):
    """Finds an element by text."""
    return driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")


def login() -> webdriver.Chrome:
    """Logs in and returns a webdriver object."""
    chrome_options = webdriver.ChromeOptions()
    if HEADLESS:
        chrome_options.add_argument("--headless")
    if MUTED:
        chrome_options.add_argument("--mute-audio")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(URL)
    driver.find_element(By.ID, "loginUsername").send_keys(USER)
    driver.find_element(By.ID, "loginPassword").send_keys(PASS)
    driver.find_element(By.ID, "loginButton").click()
    time.sleep(1)

    btn = driver.find_elements(By.ID, "alreadyOnlineContinueButton")
    if len(btn) > 0:
        btn[0].click()

    return driver


def enter_game(
    driver: webdriver.Chrome, room_name: str, room: int, password: str = ""
) -> None:
    """Enters a game from the home page."""
    driver.find_element(By.ID, "mpPlayButton").click()

    driver.find_element(By.ID, "rbSearchInput").send_keys(room_name)
    time.sleep(1)
    top = driver.find_element(By.ID, f"rbRoom-{room}")
    top.find_element(By.CLASS_NAME, "rbrJoinButton").click()

    title = driver.find_elements(By.ID, "swal2-title")
    if len(title) > 0:
        driver.find_element(By.CLASS_NAME, "swal2-input").send_keys(password)
        driver.find_element(By.CLASS_NAME, "swal2-confirm").click()

    time.sleep(1)
    ready_up(driver)


def block_recording(driver: webdriver.Chrome) -> None:
    """Blocks until it's time to start recording."""
    while True:
        try:
            t = driver.find_element(By.ID, "qpHiderText")
            txt = t.text.strip()
            # if it's showing a high number, start recording
            if txt in set(str(i) for i in range(15, 21)):
                break
            vote_skip(driver)
            ready_up(driver)
        except KeyboardInterrupt:
            driver.quit()
            exit()
        except:  # noqa: E722
            pass


def ready_up(driver: webdriver.Chrome) -> None:
    """Clicks the ready button."""
    try:
        btn = driver.find_element(By.ID, "lbStartButton")
        if btn.text.strip() == "Ready" or btn.text.strip() == "Start":
            btn.click()
    except KeyboardInterrupt:
        driver.quit()
        exit()
    except:  # noqa: E722
        pass


def vote_skip(driver: webdriver.Chrome) -> None:
    """Who has time to listen to the entire song?"""
    try:
        btn = driver.find_element(By.ID, "qpVoteSkip")
        if "toggled" not in btn.get_attribute("class").split():  # type: ignore
            btn.click()
    except KeyboardInterrupt:
        driver.quit()
        exit()
    except:  # noqa: E722
        pass


def answer(driver: webdriver.Chrome, ans: str) -> None:
    """Gives an answer."""
    box = driver.find_element(By.ID, "qpAnswerInput")
    box.send_keys(ans)
    box.send_keys(Keys.RETURN)


if __name__ == "__main__":
    driver = login()
    enter_game(
        driver,
        input("Room name? "),
        int(input("Room number? ")),
        input("Room password? "),
    )
    while True:
        try:
            block_recording(driver)
            print("starting recording...")
            data = audio.record(LEN)
            audio.sd.wait()  # block on the recording
            print("processing...")
            vol1, clip = audio.preprocess(data)
            ans = main.find_song(vol1, clip, VERBOSE)
            if audio.np.max(clip) == 128:  # 0 is at 128 because of the scaling
                print("Clip is silent. Are you sure loopback is working?")
            answer(driver, ans)
        except KeyboardInterrupt:
            driver.quit()
            exit()
        except Exception as e:
            print(e)
            ans = input("quit driver?\n")
            if len(ans) > 0 and ans[0] == "y":
                driver.quit()
