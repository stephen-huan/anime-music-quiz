# serves as the API for the website
import time, json, sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import audio
import main

URL = "https://animemusicquiz.com/"  # url of the website
LOGIN = "login.json"                 # contains the username and password
LEN = 10                             # seconds to record for
VERBOSE = True                       # whether to be verbose or not

with open(LOGIN) as f:
    login = json.load(f)
    USER, PASS = login["username"], login["password"]

def find_by_text(driver: webdriver.Chrome, text: str):
    """ Finds an element by text. """
    return driver.find_elements_by_xpath(f"//*[contains(text(), '{text}')]")

def login() -> webdriver.Chrome:
    """ Logs in and returns a webdriver object. """
    driver = webdriver.Chrome()
    driver.get(URL)
    driver.find_element_by_id("loginUsername").send_keys(USER)
    driver.find_element_by_id("loginPassword").send_keys(PASS)
    driver.find_element_by_id("loginButton").click()
    time.sleep(1)

    btn = driver.find_elements_by_id("alreadyOnlineContinueButton")
    if len(btn) > 0:
        btn[0].click()

    time.sleep(5)
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

def ready_up(driver: webdriver.Chrome) -> None:
    """ Clicks the ready button. """
    try:
        driver.find_element_by_id("lbStartButton").click()
    except:
        pass

def answer(driver: webdriver.Chrome, ans: str) -> None:
    """ Gives an answer. """
    box = driver.find_element_by_id("qpAnswerInput")
    box.send_keys(ans)
    box.send_keys(Keys.RETURN)

if __name__ == "__main__":
    driver = login()
    enter_game(driver, input("Room name? "), int(input("Room number? ")), input("Room password? "))
    while True:
        try:
            input("hit enter to begin recording...\n")
            data = audio.record(LEN)
            audio.sd.wait() # block on the recording
            print("processing...")
            vol1, clip = audio.preprocess(data)
            ans = main.find_song(vol1, clip, VERBOSE)
            answer(driver, ans)
            ready_up(driver)
        except KeyboardInterrupt:
            driver.quit()
            exit()
        except Exception as e:
            print(e)
            ans = input("quit driver?\n")
            if len(ans) > 0 and ans[0] == "y":
                driver.quit()
