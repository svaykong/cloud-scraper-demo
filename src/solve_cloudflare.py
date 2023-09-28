import random
import time
from urllib import parse
import json

from seleniumbase import SB, Driver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from .common import get_current_path2


def verify_success(sb: SB = None, driver: Driver = None, assert_element: str = None) -> None:
    if sb is not None:
        sb.assert_element(assert_element, timeout=8)
        sb.sleep(4)
    else:
        driver.assert_element(assert_element, timeout=8)
        driver.sleep(4)


def set_viewport_size(sb: SB = None, driver: Driver = None) -> None:
    random_width = 1920 + random.randint(0, 100)  # 800, 1920
    random_height = 3000 + random.randint(0, 100)  # 600, 3000

    if sb is not None:
        instance = sb
    else:
        instance = driver

    window_size = instance.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, random_width, random_height)
    instance.set_window_size(*window_size)


def use_sb(url: str, assert_element: str) -> json:
    with SB(browser="chrome",
            incognito=True,
            # headless="--headless",
            proxy="192.168.178.39:8866",
            chromium_arg="""
                --no-sandbox,
                --disable-setuid-sandbox,
                --disable-extensions,
                --disable-gpu,
                --disable-dev-shm-usage,
            """,
            ) as sb:

        set_viewport_size(sb=sb)

        sb.open(url)

        is_detected = False

        try:
            current_title = sb.get_title()
            current_source = sb.get_page_source()
            navigator_user_agent = sb.get_user_agent()
            sb.save_cookies(name="cookies_1.txt")

            verify_success(sb=sb, assert_element=assert_element)
        except Exception as e:
            print(f'{e} verify ...')
            is_detected = True
            if sb.is_element_visible('input[value*="Verify"]'):
                sb.click('input[value*="Verify"]')
                sb.sleep(5)
            elif sb.is_element_visible('iframe[title*="challenge"]'):
                sb.switch_to_frame('iframe[title*="challenge"]')
                sb.click("span.mark")
                sb.sleep(5)
            else:
                print('Detected1 ...')
                raise Exception("Detected")

            try:
                current_title = sb.get_title()
                current_source = sb.get_page_source()
                navigator_user_agent = sb.get_user_agent()
                sb.save_cookies(name="cookies_2.txt")

                # sb.save_screenshot_to_logs(name="click_box.png")
                verify_success(sb=sb, assert_element=assert_element)
            except Exception as e:
                print(f'error Detected2 ...: {e}')
                raise Exception("Detected")

            print(f'Website title: {current_title}')

        if is_detected:
            cookie_filename = get_current_path2("saved_cookies/cookies_2.txt")
        else:
            cookie_filename = get_current_path2("saved_cookies/cookies_1.txt")

        with open(cookie_filename, 'r') as f:
            cookies = json.load(f)
        print(f'cookies data: {cookies}')

        out_key = ''
        out_value = ''
        out_full_cookie = ''
        for cookie in cookies:
            for key, value in cookie.items():
                print(f'key: {key} | value: {value}')
                if key != 'name' and key != 'value':
                    continue

                if key == 'name':
                    out_key = value
                if key == 'value':
                    out_value = value
                out_full_cookie += out_key + '=' + out_value + ';'

        print(f'full cookie: {out_full_cookie}')
        new_cookie_str = out_full_cookie[:-1]

        print(f'new cookie: {new_cookie_str}')

        encode_str = parse.quote(current_source, encoding='utf-8')
        return {
            "data": encode_str,
            "title": current_title,
            "navigator_user_agent": navigator_user_agent,
            "cookies": cookies
        }


def use_driver(url: str, assert_element: str) -> json:
    driver = Driver(
        proxy="192.168.178.39:8866",
        incognito=True,
        chromium_arg="""
            --no-sandbox,
            --disable-setuid-sandbox,
            --start-maximize,
            --disable-extensions,
            --disable-gpu,
            --disable-dev-shm-usage,
        """,
    )

    set_viewport_size(driver=driver)
    driver.open(url)

    # verify assert_element
    try:
        verify_success(driver=driver, assert_element=assert_element)
    except Exception as e:
        print(f'{e}')
        print("checkbox detected...")
        print("try to click...")
        if driver.is_element_visible('input[value*="Verify"]'):
            driver.click('input[value*="Verify"]')
            driver.sleep(5)
        elif driver.is_element_visible('iframe[title*="challenge"]'):
            # find the frame
            # driver.switch_to_frame('iframe[title*="challenge"]')
            # driver.click("span.mark")
            # driver.sleep(5)

            print('WebDriverWait frame_to_be_available_and_switch_to_it...')

            # Wait for the CAPTCHA to load
            # WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
            #     (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))

            # print('WebDriverWait element_to_be_clickable...')
            # click the checkbox label
            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            #     (By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()

        else:
            print('cannot verify site')
            raise Exception("Detected")


def get_new_driver(headless: bool = True, url: str = None, assert_element: str = None) -> WebDriver:
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("start-maximized")
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    proxy = "192.168.178.39:8866"
    chrome_options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    time.sleep(2)
    wait = WebDriverWait(driver, 2)

    try:
        # assert element
        expected_element: WebElement = wait.until(EC.visibility_of(driver.find_element(By.CSS_SELECTOR, assert_element)))
        print(f'expected_element: {expected_element.is_displayed()}')

    except NoSuchElementException as e:
        print(f"assert element exception")
        print("checking checkbox exist...")

        input_verify_exist = False
        try:
            verify_element: WebElement = driver.find_element(By.CSS_SELECTOR, 'input[value*="Verify"]')
            print(f'verify_element: {verify_element.is_displayed()}')

            if verify_element.is_displayed():
                input_verify_exist = True
                verify_element.click()
                time.sleep(5)
        except NoSuchElementException as e:
            print(f"verify_element exception")
            input_verify_exist = False

        if not input_verify_exist:
            try:
                print('WebDriverWait frame_to_be_available_and_switch_to_it...')

                wait = WebDriverWait(driver, 20)
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title*="challenge"]')))

                print('WebDriverWait element_to_be_clickable...')

                # "span.mark" (got error)
                # "label.ctp-checkbox-label"
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()

                time.sleep(20)

                driver.save_screenshot("../imgs/after_click.png")

            except NoSuchElementException as e:
                print(f"iframe_element exception: {e.msg}")

    return driver


class SolveCloudflare:
    def solve(self, url=None, assert_element=None) -> json:
        print('Solve cloudflare...')

        # use_sb(url=url, assert_element=assert_element)
        # use_driver(url=url, assert_element=assert_element)

        driver = get_new_driver(headless=False, url=url, assert_element=assert_element)
        driver.quit()
