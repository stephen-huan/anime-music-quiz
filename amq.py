# serves as the API for the website
import time
from selenium import webdriver

URL = "https://animemusicquiz.com/"

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get(URL)
    time.sleep(1)
    driver.quit()
