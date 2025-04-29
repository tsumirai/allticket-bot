# USE MULTIPLE WINDOW INSTEAD OF MULTIPLE BROWSER (BUT NEED TO HANDLE RECAPTCHA FIRST)
from selenium import webdriver
# from selenium_recaptcha_solver import RecaptchaSolver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver
from selenium.webdriver.edge.options import Options as EdgeOptions
import time
import json
import os
import platform
from typing import Dict, List
from utils.general import generate_html_from_string
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
import logging
from selenium.common.exceptions import NoSuchElementException
from drivers.browser import get_driver
from login.login_handler import make_login
from seats.seat_reserver import reserve_seat_from_layout
from utils.logger import setup_logger
from utils.general import handle_cookie_popup
import json
import time

# # 1. HOW TO RECAPTCHA
# # 2. HOW TO SELECT LEVEL WHICH AVAILABLE (CHENG RECOMMEND B OVER A)
# # 3. SCRAPE THE SEAT WITH THE GIVEN PREDEFINED NUMBER 
# # 4. DEAL WITH MONEY
# # 5. TYPES ADDED TO FUNCTION

# def get_user_json()->Dict:
#     file_name = "user.json"
#     with open(file_name,"r") as f:
#         data = json.load(f)
#     return data

# def get_driver(profile="anonymous", browser="chrome"):
#     # Anonymous can be Default, Profile 1
#     # driver_path = r'C:\Program Files (x86)\chromedriver-win64\chromedriver.exe'
#     # driver_path = r'D:\myprojects\MyPython\allticket-bot\chromedriver-win64\chromedriver.exe'

#     system = platform.system()
#     print(f"Profile: {profile}, Browser: {browser}")

#      # 自动设置 Chrome 驱动路径
#     if system == "Windows":
#         chrome_driver_path = r'D:\myprojects\MyPython\allticket-bot\chromedriver-win64\chromedriver.exe'
#         chrome_user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

#         edge_driver_path = r'D:\myprojects\MyPython\allticket-bot\msedgedriver.exe'
#         edge_user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")
#     elif system == "Darwin":
#         project_root = os.path.dirname(os.path.abspath(__file__))
#         print(project_root)
#         chrome_driver_path = os.path.join(project_root,"chromedriver-mac-arm64","chromedriver")
#         chrome_user_data_path = os.path.expanduser("~/Library/Application Support/Google/Chrome")

#         edge_driver_path = os.path.join(project_root, "msedgedriver-mac-arm64", "msedgedriver")
#         edge_user_data_path = os.path.expanduser("~/Library/Application Support/Microsoft Edge")
#     else:
#         raise RuntimeError("当前系统不受支持（仅支持 Windows 和 macOS）")
    
#     if browser == "chrome":
#         options = webdriver.ChromeOptions()
#         driver_path = chrome_driver_path
#         user_data_path = chrome_user_data_path
#     elif browser == "edge":
#         options = EdgeOptions()
#         driver_path = edge_driver_path
#         user_data_path = edge_user_data_path
#     else: 
#         raise ValueError("browser 参数只能是 'chrome' 或 'edge'")
    
#     # options = webdriver.ChromeOptions()
#     options.add_experimental_option('excludeSwitches', ['enable-logging'])
#     options.add_argument("--disable-extensions")
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_argument("start-maximized")
#     if profile != "anonymous":
#         # options.add_argument(r'--user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data');
#         options.add_argument(f"--user-data-dir={user_data_path}")
#         options.add_argument(f"--profile-directory={profile}")
    
#     service = Service(executable_path=driver_path)

#     if browser == "chrome":
#         driver = webdriver.Chrome(service=service, options=options)
#     elif browser == "edge":
#         driver = webdriver.Edge(service=service, options=options)
   
#     return driver

# def get_all_child_element(parent_element):
#     return parent_element.find_elements(By.XPATH,".//*")

# def handle_cookie_popup(driver):
#     try:
#         # accept_all_button = driver.find_element(By.CSS_SELECTOR, ".cc-btn.cc-allow")
#         # accept_all_button.click()
#         # print("已点击 cookie 同意按钮。")
#         allow_button = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.CLASS_NAME, "cc-allow"))
#         )
#         allow_button.click()
#         print("已点击 cookie 同意按钮。")
#     except Exception as e:
#         print("未发现 cookie 弹窗，跳过处理。")


# def make_login(driver, recaptcha_solver, data:Dict):
#     """Login from the allticket.com page
    
#     Problem : Recaptcha is able to detect recaptcha_solver automation 
#     Add manual way to let the user solve ReCAPTCHA
    
#     Keyword arguments:
#     driver
#     data - Dictionary contains email, password
#     Return: return_description
#     """
#     # Get into Email/Password Login system
    
#     login_button = driver.find_element(by=By.ID, value="loginBtn")
#     login_button.click()
    
#     # Locate the element first
#     email_login_textbox = driver.find_element(by=By.ID, value="email-login")
#     password_login_textbox = driver.find_element(by=By.ID, value="password-login")
#     signin_button = driver.find_element(By.XPATH, "//button[contains(@class, 'signin-button')]")
    
#     # Fill element with data
#     email_login_textbox.send_keys(data["email"])
#     password_login_textbox.send_keys(data["password"])
    
#     # Solve ReCAPTCHA
#     recaptcha_iframe = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//iframe[@title='reCAPTCHA']")))
#     # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
#     time.sleep(5)
#     recaptcha_solver.click_recaptcha_v2(iframe=recaptcha_iframe)
#     # Now do Selenium
#     driver.switch_to.default_content()
#     signin_button.click()


# def reserve_seat_from_layout(app_seat_layout_element, 
#                              limited_seat_num:int = 4, 
#                              strategy="simple"):
    
#     # Wait until seat layout appeared (For sit strategy)
#     table_layout_element = app_seat_layout_element.find_element(By.TAG_NAME, "table")
#     reserved_count = 0

#     # Get all clickable seat element (Always have text inside svg)
#     all_seat_xpath = "//tbody/tr/td/div"
#     available_seat_xpath = all_seat_xpath+"/*[local-name() = 'svg']/*[local-name() = 'text']"
#     available_seat_elements = table_layout_element.find_elements(By.XPATH, available_seat_xpath)
#     # Loop though 
#     for available_seat_element in available_seat_elements:
#         # If no popup was found, then continue clicking
#         try:
#             available_seat_element.click()
#             reserved_count += 1
#             if reserved_count == limited_seat_num:
#                 break
#         # If it reachs the limit
#         except ElementClickInterceptedException as e:
#             pass
        
# # Setup logging to allow us to spot the bug
# def main():
#     logger = logging.getLogger(__name__)
#     logging.basicConfig(filename=f'log/recent.log', encoding='utf-8', level=logging.DEBUG)

#     data = get_user_json()
    
#     # Avoid RECAPTCHA By logging in Google Profile
#     profile = data["profile"]
#     event_name = data['event_name']
#     prior_seat_types = data.get("prior_seat_types",[])
#     payment_method = data.get("payment_method","cash")
#     browser = data.get("browser", "chrome")

#     driver = get_driver(profile=profile, browser=browser)
    
#     # Setup the common wait
#     wait = WebDriverWait(driver, 10)
#     driver.implicitly_wait(3)

#     # Now
#     event_url = f"https://www.allticket.com/event/{event_name}"
#     driver.get(event_url)

#     # Start
#     # buy_button = driver.find_element(By.XPATH,"/html/body/app-root/app-event-info/div/div[2]/div[2]/div/div[5]/div/button")
#     # buy_button.click()
#     buy_button_xpath = "/html/body/app-root/app-event-info/div/div[2]/div[2]/div/div[5]/div/button"
#     while True:
#         try:
#             buy_button = driver.find_element(By.XPATH, buy_button_xpath)
#             button_text = buy_button.text.strip().upper()

#             if button_text == "BUY NOW":
#                 print("🎯 检测到 BUY NOW 按钮，开始购票流程。")
#                 buy_button.click()
#                 break
#             elif button_text == "COMING SOON":
#                 print("⏳ 仍然是 COMING SOON，3秒后刷新页面继续等待...")
#                 time.sleep(3)
#                 driver.refresh()
#             else:
#                 print(f"⚠️ 检测到未知按钮：{button_text}，3秒后刷新...")
#                 time.sleep(3)
#                 driver.refresh()
#         except Exception as e:
#             print(f"⚠️ 检测按钮失败：{e}，3秒后刷新...")
#             time.sleep(3)
#             driver.refresh()

#     # Read and Agree the condition
#     generate_html_from_string(driver.page_source)

#     try:
#         accept_consent_checkbox = driver.find_element(By.CSS_SELECTOR, "label[for='acceptConsent']")
#         accept_consent_checkbox.click()

#         confirm_button = driver.find_element(By.XPATH, "//span[text()=' Confirm ']/parent::*")
#         confirm_button.click()
#         print("同意协议并点击确认按钮。")
#     except Exception as e:
#         print("未发现同意协议的勾选框和按钮，跳过。")

#     # Land to reserve page as Some concerts have more than 1 time, they will ask before to check seat available
#     # TODO : If the confirmed button is still not done, then, it is possible that the popup window will be shown, Click yes to wait for a few minute

#     handle_cookie_popup(driver)

#     time_index = data.get("time_index")
#     if time_index:
#         # Assume that there is time_index if it was provided
#         select_time_container_xpath = "/html/body/app-root/app-booking/div[3]/div[1]"
#         select_time_container = wait.until(EC.presence_of_element_located((By.XPATH, select_time_container_xpath)))
#         select_time_button_xpath = f"{select_time_container_xpath}/div[{time_index+1}]/div/label"
#         select_time_button_xpath = wait.until(EC.presence_of_element_located((By.XPATH, select_time_container_xpath)))
#         select_time_button_xpath.click()

#     # Performing Check Seat Available being shown
#     check_seat_available_button_xpath = "//button[contains(text(),'CHECK SEAT AVAILABLE')]"
#     check_seat_available_button = wait.until(EC.presence_of_element_located((By.XPATH, check_seat_available_button_xpath)))
#     check_seat_available_button.click()

#     # Now, all seats from each zone is being shown

#     # Get Seat Available Container which containing 2 column : SEAT TYPE and Number of Available 
#     seat_ava_container_xpath = '/html/body/app-root/app-booking/div[3]/div[2]/app-get-seat-available'
#     seat_ava_container_element = wait.until(EC.presence_of_element_located((By.XPATH, seat_ava_container_xpath)))

#     # Iterating all seats type via map image
#     seat_ava_map_element = wait.until(EC.presence_of_element_located((By.ID, "zone")))
#     seat_ava_map_element = seat_ava_map_element.find_element(By.XPATH,".//div/p/map")


#     """
#     seat_ava_map_element : 
#         <area class="p_A1" coords="102,130,47,173,47,200,178,199,178,130" data-zone="A1" shape="poly">
#         <area class="p_A2" coords="102,130,47,173,47,200,178,199,178,130" data-zone="A1" shape="poly">
#     """

#     # prior_seat_types = ["A1"]

#     # Start by iterating in these seat type
#     for prior_seat_type in prior_seat_types:
#         seat_ava_prior_map_element = seat_ava_map_element.find_element(By.XPATH, f'.//*[@class="p_{prior_seat_type}"]')
#         # 尝试隐藏遮挡元素
#         try:
#             h3_overlay = driver.find_element(By.CSS_SELECTOR, "h3.is-size-5.font-weight-bold")
#             driver.execute_script("arguments[0].style.display='none';", h3_overlay)
#             print("已隐藏 h3 遮挡元素")
#         except:
#             print("未找到 h3 遮挡元素，跳过")
#         seat_ava_prior_map_element.click()


#     # Wait until seat layout appeared (For sit strategy)

#     # Click all
#     app_seat_layout_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-seat-layout")))
#     # Start reserving ticket from app seat layout element of that seat type 
#     reserve_seat_from_layout(app_seat_layout_element)

#     booking_button = driver.find_element(By.XPATH,"//span[contains(text(), 'Booking')]/parent::button")
#     booking_button.click()

#     print("✅ 已点击预订按钮，程序将在付款页停留，请手动付款。")

#     input("🛑 手动付款完成后请按 Enter 关闭程序和浏览器...")
#     return

#     # Now, looking for App summary
#     wait = WebDriverWait(driver, 30)
#     app_reserve_summary_element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-reserve-summary"))) 

#     # Select Payment method
#     payment_method_index = {"cash" : 1, "promptpay" : 4}
#     payment_method_xpath= f"//div[1]/div[2]/div[1]/div/div/div[2]/div[2]/div[{payment_method_index[payment_method]}]/label"
#     payment_method_element = app_reserve_summary_element.find_element(By.XPATH,payment_method_xpath)
#     payment_method_element.click()

#     # Select Payment method
#     payment_agree_button = driver.find_element(By.CSS_SELECTOR,"label[for='checkAgree']")
#     payment_agree_button.click()

#     booking_button = app_reserve_summary_element.find_element(By.XPATH,"//span[contains(text(), 'Payment')]/parent::button")
#     booking_button.click()

#     confirm_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='swal2-confirm swal2-styled']"))) 
#     confirm_button.click()

#     # Not quit until.
#     time.sleep(1000000)
    
#     # driver.quit()

# main()



def get_user_json():
    with open("user.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    logger = setup_logger()

    data = get_user_json()
    driver = get_driver(profile=data.get("profile", "anonymous"), browser=data.get("browser", "chrome"))
    driver.implicitly_wait(3)

    # # 登录
    # from utils.recaptcha_solver import RecaptchaSolver
    # solver = RecaptchaSolver(driver)
    # make_login(driver, solver, data)

    event_url = f"https://www.allticket.com/event/{data['event_name']}"
    driver.get(event_url)

    wait = WebDriverWait(driver, 10)

    # Start
    # buy_button = driver.find_element(By.XPATH,"/html/body/app-root/app-event-info/div/div[2]/div[2]/div/div[5]/div/button")
    # buy_button.click()
    buy_button_xpath = "/html/body/app-root/app-event-info/div/div[2]/div[2]/div/div[5]/div/button"
    while True:
        try:
            buy_button = driver.find_element(By.XPATH, buy_button_xpath)
            button_text = buy_button.text.strip().upper()

            if button_text == "BUY NOW":
                print("🎯 检测到 BUY NOW 按钮，开始购票流程。")
                buy_button.click()
                break
            elif button_text == "COMING SOON":
                print("⏳ 仍然是 COMING SOON，3秒后刷新页面继续等待...")
                time.sleep(3)
                driver.refresh()
            else:
                print(f"⚠️ 检测到未知按钮：{button_text}，3秒后刷新...")
                time.sleep(3)
                driver.refresh()
        except Exception as e:
            print(f"⚠️ 检测按钮失败：{e}，3秒后刷新...")
            time.sleep(3)
            driver.refresh()

    # Read and Agree the condition
    generate_html_from_string(driver.page_source)

    try:
        accept_consent_checkbox = driver.find_element(By.CSS_SELECTOR, "label[for='acceptConsent']")
        accept_consent_checkbox.click()

        confirm_button = driver.find_element(By.XPATH, "//span[text()=' Confirm ']/parent::*")
        confirm_button.click()
        print("同意协议并点击确认按钮。")
    except Exception as e:
        print("未发现同意协议的勾选框和按钮，跳过。")

    # Land to reserve page as Some concerts have more than 1 time, they will ask before to check seat available
    # TODO : If the confirmed button is still not done, then, it is possible that the popup window will be shown, Click yes to wait for a few minute

    handle_cookie_popup(driver)

    time_index = data.get("time_index")
    if time_index:
        # Assume that there is time_index if it was provided
        select_time_container_xpath = "/html/body/app-root/app-booking/div[3]/div[1]"
        select_time_container = wait.until(EC.presence_of_element_located((By.XPATH, select_time_container_xpath)))
        select_time_button_xpath = f"{select_time_container_xpath}/div[{time_index+1}]/div/label"
        select_time_button_xpath = wait.until(EC.presence_of_element_located((By.XPATH, select_time_container_xpath)))
        select_time_button_xpath.click()

    # Performing Check Seat Available being shown
    check_seat_available_button_xpath = "//button[contains(text(),'CHECK SEAT AVAILABLE')]"
    check_seat_available_button = wait.until(EC.presence_of_element_located((By.XPATH, check_seat_available_button_xpath)))
    check_seat_available_button.click()

    # Now, all seats from each zone is being shown

    # Get Seat Available Container which containing 2 column : SEAT TYPE and Number of Available 
    seat_ava_container_xpath = '/html/body/app-root/app-booking/div[3]/div[2]/app-get-seat-available'
    seat_ava_container_element = wait.until(EC.presence_of_element_located((By.XPATH, seat_ava_container_xpath)))

    # Iterating all seats type via map image
    seat_ava_map_element = wait.until(EC.presence_of_element_located((By.ID, "zone")))
    seat_ava_map_element = seat_ava_map_element.find_element(By.XPATH,".//div/p/map")


    """
    seat_ava_map_element : 
        <area class="p_A1" coords="102,130,47,173,47,200,178,199,178,130" data-zone="A1" shape="poly">
        <area class="p_A2" coords="102,130,47,173,47,200,178,199,178,130" data-zone="A1" shape="poly">
    """

    # prior_seat_types = ["A1"]

    # Start by iterating in these seat type
    prior_seat_types = data.get("prior_seat_types",[])
    for prior_seat_type in prior_seat_types:
        seat_ava_prior_map_element = seat_ava_map_element.find_element(By.XPATH, f'.//*[@class="p_{prior_seat_type}"]')
        # 尝试隐藏遮挡元素
        try:
            h3_overlay = driver.find_element(By.CSS_SELECTOR, "h3.is-size-5.font-weight-bold")
            driver.execute_script("arguments[0].style.display='none';", h3_overlay)
            print("已隐藏 h3 遮挡元素")
        except:
            print("未找到 h3 遮挡元素，跳过")
        seat_ava_prior_map_element.click()


    # Wait until seat layout appeared (For sit strategy)

    # Click all
    app_seat_layout_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-seat-layout")))
    # Start reserving ticket from app seat layout element of that seat type 
    reserve_seat_from_layout(app_seat_layout_element)

    booking_button = driver.find_element(By.XPATH,"//span[contains(text(), 'Booking')]/parent::button")
    booking_button.click()

    print("✅ 已点击预订按钮，程序将在付款页停留，请手动付款。")

    input("🛑 手动付款完成后请按 Enter 关闭程序和浏览器...")
    return

    # Now, looking for App summary
    wait = WebDriverWait(driver, 30)
    app_reserve_summary_element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-reserve-summary"))) 

    # Select Payment method
    payment_method_index = {"cash" : 1, "promptpay" : 4}
    payment_method_xpath= f"//div[1]/div[2]/div[1]/div/div/div[2]/div[2]/div[{payment_method_index[payment_method]}]/label"
    payment_method_element = app_reserve_summary_element.find_element(By.XPATH,payment_method_xpath)
    payment_method_element.click()

    # Select Payment method
    payment_agree_button = driver.find_element(By.CSS_SELECTOR,"label[for='checkAgree']")
    payment_agree_button.click()

    booking_button = app_reserve_summary_element.find_element(By.XPATH,"//span[contains(text(), 'Payment')]/parent::button")
    booking_button.click()

    confirm_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='swal2-confirm swal2-styled']"))) 
    confirm_button.click()

    # Not quit until.
    time.sleep(1000000)
    
    # driver.quit()

    try:
        # 关闭 Cookie 弹窗（如果有）
        handle_cookie_popup(driver)

        # 点击 "立即购票" 按钮
        buy_now_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "productDetail-ticketBtn")))
        buy_now_button.click()
        logger.info("点击了立即购票按钮")
        
        # 选择场次（如有）
        ticket_dates = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ticketDate-time")))
        if ticket_dates:
            if data.get("datetime") is not None:
                found = False
                for date_element in ticket_dates:
                    if data["datetime"] in date_element.text:
                        date_element.click()
                        logger.info(f"选择了场次：{date_element.text}")
                        found = True
                        break
                if not found:
                    logger.warning("没有找到匹配的场次，默认选择第一个")
                    ticket_dates[0].click()
            else:
                logger.info("未指定场次，默认选择第一个")
                ticket_dates[0].click()

        time.sleep(1)

        # 点击 "我要购票"
        to_buy_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ticketDate-submitBtn")))
        to_buy_button.click()
        logger.info("点击了我要购票按钮")

        # 选择票种
        ticket_types = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ticket-kind-row")))
        for ticket in ticket_types:
            if data["ticket_type"] in ticket.text:
                plus_button = ticket.find_element(By.CLASS_NAME, "ticket-kind-row-plusBtn")
                plus_button.click()
                logger.info(f"选择票种：{ticket.text}")
                break

        # 确认选票
        confirm_ticket_button = driver.find_element(By.CLASS_NAME, "next-btn-primary")
        confirm_ticket_button.click()
        logger.info("确认选择票种")

        # 选择座位区域
        seat_area_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ticket-area-item")))
        if seat_area_elements:
            if "seat_priority" in data:
                found_area = False
                for priority_area in data["seat_priority"]:
                    for area_element in seat_area_elements:
                        if priority_area in area_element.text:
                            area_element.click()
                            logger.info(f"优先选择了区域：{priority_area}")
                            found_area = True
                            break
                    if found_area:
                        break
                if not found_area:
                    logger.warning("优先区域未找到，默认选择第一个区域")
                    seat_area_elements[0].click()
            else:
                seat_area_elements[0].click()
                logger.info("未指定优先区域，默认选择第一个区域")
        
        # 点击进入座位图
        choose_seat_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ticket-area-submitBtn")))
        choose_seat_button.click()
        logger.info("点击了进入座位图按钮")

        # 抢座位
        seat_layout = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "app-seats-layout")))
        reserve_seat_from_layout(seat_layout, limited_seat_num=data.get("seat_num", 4))
        logger.info("完成选座")

        # 点击下一步
        next_step_button = driver.find_element(By.CLASS_NAME, "ticket-seat-nextBtn")
        next_step_button.click()
        logger.info("点击了下一步按钮")

        # 进入结账页面，选择付款方式
        time.sleep(2)
        payment_methods = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "paymentMethod-item")))
        for method in payment_methods:
            if data["payment_method"] in method.text:
                method.click()
                logger.info(f"选择支付方式：{data['payment_method']}")
                break
        
        # 同意协议
        agree_checkbox = driver.find_element(By.NAME, "chkAccept")
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
            logger.info("同意购票协议")

        # 点击 "立即结账"
        checkout_button = driver.find_element(By.CLASS_NAME, "payment-checkout-btn")
        checkout_button.click()
        logger.info("点击了立即结账按钮")

        logger.info("抢票流程完成，等待支付！")
    
    except Exception as e:
        logger.error(f"抢票过程中出错：{str(e)}")
        driver.save_screenshot("error.png")
        raise

if __name__ == "__main__":
    main()
