from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException

def reserve_seat_from_layout(app_seat_layout_element, limited_seat_num=4):
    table_layout_element = app_seat_layout_element.find_element(By.TAG_NAME, "table")
    available_seat_xpath = "//tbody/tr/td/div/*[local-name() = 'svg']/*[local-name() = 'text']"
    available_seat_elements = table_layout_element.find_elements(By.XPATH, available_seat_xpath)
    
    reserved_count = 0
    for seat in available_seat_elements:
        try:
            seat.click()
            reserved_count += 1
            if reserved_count >= limited_seat_num:
                break
        except ElementClickInterceptedException:
            continue
