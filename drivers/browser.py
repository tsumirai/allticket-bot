from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from config.settings import *

def get_driver(profile="anonymous", browser="chrome"):
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        driver_path = CHROME_DRIVER_PATH
        user_data_path = CHROME_USER_DATA_PATH
    elif browser == "edge":
        options = EdgeOptions()
        driver_path = EDGE_DRIVER_PATH
        user_data_path = EDGE_USER_DATA_PATH
    else:
        raise ValueError("browser 参数只能是 'chrome' 或 'edge'")

    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("start-maximized")

    if profile != "anonymous":
        options.add_argument(f"--user-data-dir={user_data_path}")
        options.add_argument(f"--profile-directory={profile}")

    service = Service(executable_path=driver_path)

    if browser == "chrome":
        return webdriver.Chrome(service=service, options=options)
    else:
        return webdriver.Edge(service=service, options=options)
