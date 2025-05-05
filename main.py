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
from login.login_handler import manual_login
from seats.seat_reserver import reserve_seat_from_layout
from utils.logger import setup_logger
from utils.general import handle_cookie_popup
import json
import time

def get_user_json():
    with open("user.json", "r", encoding="utf-8") as f:
        return json.load(f)
    
def wait_for_button_loaded(driver, timeout=30):
    """
    等待 buttonWrapper 的 class 属性中不再包含 'spinner-loading'
    表示按钮已完全加载好
    """
    print("⌛ 等待按钮加载完成（spinner 消失）...")
    
    WebDriverWait(driver, timeout).until(
        lambda d: "spinner-loading" not in d.find_element(By.ID, "buttonWrapper").get_attribute("class")
    )

    print("✅ 按钮已加载完成。")

def click_buy_button(driver):
    buy_button_xpath = "//div[@id='buttonWrapper']//button"
    while True:
        try:
            buy_button = driver.find_element(By.XPATH, buy_button_xpath)
            button_text = buy_button.text.strip().upper()

            if button_text == "BUY NOW":
                print("🎯 检测到 BUY NOW 按钮，开始购票流程。")
                buy_button.click()
                break
            elif button_text == "COMING SOON":
                print("⏳ 仍然是 COMING SOON，1秒后刷新页面继续等待...")
                time.sleep(1)
                driver.refresh()
                wait_for_button_loaded(driver)
            else:
                print(f"⚠️ 检测到未知按钮：{button_text}，3秒后刷新...")
                time.sleep(3)
                driver.refresh()
                wait_for_button_loaded(driver)
        except Exception as e:
            print(f"⚠️ 检测按钮失败：{e}，3秒后刷新...")
            time.sleep(3)
            driver.refresh()
            wait_for_button_loaded(driver)

def select_show_time(driver, wait, time_index):
    """
    选择演出场次（如果有多个场次）。
    :param driver: Selenium driver 实例
    :param wait: WebDriverWait 实例
    :param time_index: 想要选择的场次序号（从 0 开始）
    """
    if time_index is None:
        print("ℹ️ 未设置 time_index，跳过场次选择。")
        return

    try:
        # 获取所有场次的 input radio 元素
        radio_inputs = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "input.custom-control-input[type='radio']")
        ))
        
        if time_index >= len(radio_inputs) + 1:
            print(f"⚠️ 提供的 time_index={time_index} 超出可用场次范围（共 {len(radio_inputs)} 场）。")
            return

        # 获取目标 input 元素并点击对应 label
        target_input = radio_inputs[time_index-1]
        label_for = target_input.get_attribute("id")
        label_element = driver.find_element(By.CSS_SELECTOR, f"label[for='{label_for}']")
        label_element.click()

        print(f"✅ 成功点击第 {time_index} 个场次：label[for='{label_for}']")
    except Exception as e:
        print(f"❌ 选择场次失败：{e}")

def get_seat_availability(driver):
    """解析座位可用性容器，返回 {区域: 数量} 的字典"""
    seat_avail = {}
    try:
        # 定位到座位可用性容器
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//app-get-seat-available//div[@class="card-body"]'))
        )
        
        # 提取所有区域行
        rows = container.find_elements(By.XPATH, 
            './/div[contains(@class, "row") and contains(@class, "col-12") and contains(@class, "m-0")]')
        
        for row in rows:
            try:
                # 提取区域名称
                zone_span = row.find_element(By.XPATH, './/div[@class="col-5 px-0 seat-ava"]//span')
                zone = zone_span.text.strip()
                
                # 提取可用数量（兼容 success/danger 状态）
                avail_span = row.find_element(By.XPATH, './/div[@class="col-7 px-0"]//span')
                avail = int(avail_span.text.strip()) if avail_span.text.strip().isdigit() else 0
                
                seat_avail[zone] = avail
            except:
                continue
    except Exception as e:
        print("解析座位可用性失败:", str(e))
    
    return seat_avail


def main():
    logger = setup_logger()

    data = get_user_json()

    browser = data.get("browser", "chrome")
    if browser == "chrome":
        profile=data.get("chrome_profile", "anonymous")
    elif browser == "edge":
        profile=data.get("edge_profile", "anonymous")
    else:
        profile = "anonymous"

    driver = get_driver(profile=profile, browser=browser)
    print("get driver success")
    driver.implicitly_wait(3)

    # # 登录
    # from utils.recaptcha_solver import RecaptchaSolver
    # solver = RecaptchaSolver(driver)
    # make_login(driver, solver, data)

    event_url = f"https://www.allticket.com/event/{data['event_name']}"
    driver.get(event_url)

    wait = WebDriverWait(driver, 10)

    manual_login(driver)

    # Start
    # buy_button = driver.find_element(By.XPATH,"/html/body/app-root/app-event-info/div/div[2]/div[2]/div/div[5]/div/button")
    # buy_button.click()
    # 等待页面初始加载完成，避免 spinner 误判
    wait_for_button_loaded(driver)

    # 进入按钮点击逻辑
    click_buy_button(driver)

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

    # time_index = data.get("time_index")
    # if time_index:
    #     # Assume that there is time_index if it was provided
    #     select_time_container_xpath = "/html/body/app-root/app-booking/div[3]/div[1]"
    #     select_time_container = wait.until(EC.presence_of_element_located((By.XPATH, select_time_container_xpath)))
    #     select_time_button_xpath = f"{select_time_container_xpath}/div[{time_index+1}]/div/label"
    #     select_time_button_xpath = wait.until(EC.presence_of_element_located((By.XPATH, select_time_container_xpath)))
    #     select_time_button_xpath.click()

    time_index = data.get("time_index")
    select_show_time(driver, wait, time_index)

    # Performing Check Seat Available being shown
    check_seat_available_button_xpath = "//button[contains(text(),'CHECK SEAT AVAILABLE')]"
    check_seat_available_button = wait.until(EC.presence_of_element_located((By.XPATH, check_seat_available_button_xpath)))
    check_seat_available_button.click()

    # Now, all seats from each zone is being shown

    # Get Seat Available Container which containing 2 column : SEAT TYPE and Number of Available 
    # seat_ava_container_xpath = '/html/body/app-root/app-booking/div[3]/div[2]/app-get-seat-available'
    # seat_ava_container_element = wait.until(EC.presence_of_element_located((By.XPATH, seat_ava_container_xpath)))

    # # Iterating all seats type via map image
    # seat_ava_map_element = wait.until(EC.presence_of_element_located((By.ID, "zone")))
    # seat_ava_map_element = seat_ava_map_element.find_element(By.XPATH,".//div/p/map")


    # """
    # seat_ava_map_element : 
    #     <area class="p_A1" coords="102,130,47,173,47,200,178,199,178,130" data-zone="A1" shape="poly">
    #     <area class="p_A2" coords="102,130,47,173,47,200,178,199,178,130" data-zone="A1" shape="poly">
    # """

    # # prior_seat_types = ["A1"]

    # # Start by iterating in these seat type
    prior_seat_types = data.get("prior_seat_types",[])
    # for prior_seat_type in prior_seat_types:
    #     seat_ava_prior_map_element = seat_ava_map_element.find_element(By.XPATH, f'.//*[@class="p_{prior_seat_type}"]')
    #     # 尝试隐藏遮挡元素
    #     try:
    #         h3_overlay = driver.find_element(By.CSS_SELECTOR, "h3.is-size-5.font-weight-bold")
    #         driver.execute_script("arguments[0].style.display='none';", h3_overlay)
    #         print("已隐藏 h3 遮挡元素")
    #     except:
    #         print("未找到 h3 遮挡元素，跳过")
    #     seat_ava_prior_map_element.click()

    max_retries = 3
    retry_count = 0
    success = False

    while retry_count < max_retries and not success:
        seat_availability = get_seat_availability(driver)
        
        # 遍历优先区域
        for seat_type in prior_seat_types:
            available = seat_availability.get(seat_type, 0)
            if available <= 0:
                continue
                
            try:
                # 使用层级定位减少定位失败概率
                map_container = driver.find_element(By.ID, "zone")
                seat_element = map_container.find_element(
                    By.XPATH, f'.//area[@data-zone="{seat_type}"]')
                
                # 先滚动到可视区域
                # driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", map_container)
                
                # 带高亮效果的点击（调试用）
                # driver.execute_script("arguments[0].style.outline='3px solid red';", seat_element)
                seat_element.click()
                
                # # 等待座位布局加载
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, "//seat-layout"))
                # )
                success = True
                break
            except Exception as e:
                print(f"区域 {seat_type} 选择失败: {str(e)}")
        
        # 刷新逻辑
        if not success:
            print("尝试刷新数据...")
            try:
                driver.find_element(
                    By.XPATH, '//button[contains(., "CHECK SEAT AVAILABLE")]'
                ).click()
                # 等待刷新完成
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(map_container)
                )
                retry_count += 1
            except Exception as e:
                print("刷新失败:", e)
                break

    if not success:
        print("错误：所有区域不可用且达到最大重试次数")
        return
        # 这里可以添加失败处理逻辑
    # else:
    #     # 后续座位选择逻辑
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, "//seat-layout"))
    #     )
    #     print("进入座位选择界面...")

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
