from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def manual_login(driver):
    # 登录检测逻辑
    if not is_logged_in(driver):
        print("未检测到登录，准备点击登录按钮...")
        try:
            login_button = driver.find_element(By.ID, "loginBtn")
            login_button.click()
            wait_for_login(driver)
        except Exception as e:
            print(f"点击登录按钮失败: {e}")
            driver.quit()
            return
    else:
        print("已登录，跳过登录步骤。")

def is_logged_in(driver):
    """
    检测是否登录成功：页面上是否有用户菜单（如用户名）
    """
    try:
        driver.find_element(By.CLASS_NAME, "userMenu")
        return True
    except:
        return False

def wait_for_login(driver, timeout=180):
    """
    等待用户在指定时间内完成登录
    """
    print("请手动完成登录...")
    WebDriverWait(driver, timeout).until(lambda d: is_logged_in(d))
    print("检测到已登录。")

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
