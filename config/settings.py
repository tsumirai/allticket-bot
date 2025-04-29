import os
import platform

SYSTEM = platform.system()

if SYSTEM == "Windows":
    CHROME_DRIVER_PATH = r'D:\myprojects\MyPython\allticket-bot\chromedriver-win64\chromedriver.exe'
    EDGE_DRIVER_PATH = r'D:\myprojects\MyPython\allticket-bot\msedgedriver.exe'
    CHROME_USER_DATA_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    EDGE_USER_DATA_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")
elif SYSTEM == "Darwin":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CHROME_DRIVER_PATH = os.path.join(PROJECT_ROOT, "chromedriver-mac-arm64", "chromedriver")
    EDGE_DRIVER_PATH = os.path.join(PROJECT_ROOT, "msedgedriver-mac-arm64", "msedgedriver")
    CHROME_USER_DATA_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    EDGE_USER_DATA_PATH = os.path.expanduser("~/Library/Application Support/Microsoft Edge")
else:
    raise RuntimeError("当前系统不受支持（仅支持 Windows 和 macOS）")
