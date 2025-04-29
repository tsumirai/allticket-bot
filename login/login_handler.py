from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def make_login(driver, recaptcha_solver, data, timeout=10):
    wait = WebDriverWait(driver, timeout)
    
    driver.find_element(By.ID, "loginBtn").click()
    driver.find_element(By.ID, "email-login").send_keys(data["email"])
    driver.find_element(By.ID, "password-login").send_keys(data["password"])
    
    try:
        iframe = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[@title='reCAPTCHA']")))
        time.sleep(5)
        recaptcha_solver.click_recaptcha_v2(iframe=iframe)
        driver.switch_to.default_content()
    except Exception:
        print("未检测到ReCAPTCHA，直接继续登录")
    
    driver.find_element(By.XPATH, "//button[contains(@class, 'signin-button')]").click()
