from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def generate_html_from_string(html_string,out="log/log.html"):
    soup = BeautifulSoup(html_string, "html.parser")
    with open(out,"w",encoding="utf-8") as f:
        f.write(str(soup.prettify()))

def handle_cookie_popup(driver):
    try:
        # accept_all_button = driver.find_element(By.CSS_SELECTOR, ".cc-btn.cc-allow")
        # accept_all_button.click()
        # print("已点击 cookie 同意按钮。")
        allow_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cc-allow"))
        )
        allow_button.click()
        print("已点击 cookie 同意按钮。")
    except Exception as e:
        print("未发现 cookie 弹窗，跳过处理。")