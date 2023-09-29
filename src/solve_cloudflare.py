import random

from .common import get_current_path, get_current_path2
from urllib import parse
import json
from seleniumbase import SB, BaseCase
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def verify_sb_success(sb: SB, assert_element: str) -> None:
    sb.assert_element(assert_element, timeout=8)
    sleep(4)


def verify_success(driver: webdriver, assert_element: str) -> None:
    element = driver.find_element(By.CSS_SELECTOR, assert_element)
    

def set_viewport_size(sb: SB, width: int, height: int) -> None:
    random_width = 1920 + random.randint(0, 100)  # 800, 1920
    random_height = 3000 + random.randint(0, 100)  # 600, 3000
    window_size = sb.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, random_width, random_height)
    sb.set_window_size(*window_size)


def set_viewport_size2(driver: webdriver) -> None:
    random_width = 1920 + random.randint(0, 100)  # 800, 1920
    random_height = 3000 + random.randint(0, 100)  # 600, 3000
    window_size = driver.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, random_width, random_height)
    driver.set_window_size(*window_size)


class SolveCloudflare(BaseCase):
    def __init__(self):
        self.headless = False
        print('SolveCloudflare __init__')

    @staticmethod
    def use_sb() -> dict:
        is_detected = False
        with SB(
                uc_cdp=False,
                incognito=True,
                browser="chrome",
                agent=user_agent,
                proxy=proxy,
                headless="--headless",
                chromium_arg="""
                    --no-sandbox, 
                    --single-process,
                    --disable-dev-shm-usage,
                    --disable-setuid-sandbox,
                    --disable-extensions,
                    --disable-gpu,
                """,
                ) as sb:
        
            stealth(
                sb.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                run_on_insecure_origins=True
            )

            sb.clear_all_cookies()
            sb.clear_local_storage()
            sb.clear_session_storage()

            set_viewport_size(sb, random_width, random_height)

            sb.open(url)

            try:
                current_title = sb.get_title()
                current_source = sb.get_page_source()
                navigator_user_agent = sb.get_user_agent()
                sb.save_cookies(name="cookies_1.txt")

                verify_sb_success(sb=sb, assert_element=assert_element)
            except Exception as e:
                print(f'{e} verify ...')
                is_detected = True
                if sb.is_element_visible('input[value*="Verify"]'):
                    sb.click('input[value*="Verify"]')
                elif sb.is_element_visible('iframe[title*="challenge"]'):
                    sb.switch_to_frame('iframe[title*="challenge"]')
                    sb.click("span.mark")
                else:
                    print('Detected1 ...')
                    raise Exception("Detected")
                try:
                    # waiting finished loaded before verify again...
                    print('waiting finished loaded before verify again...')
                    sb.sleep(5)

                    current_title = sb.get_title()
                    current_source = sb.get_page_source()
                    navigator_user_agent = sb.get_user_agent()
                    sb.save_cookies(name="cookies_2.txt")

                    # sb.save_screenshot_to_logs(name="click_box.png")
                    verify_sb_success(sb=sb, assert_element=assert_element)
                except Exception as e:
                    print(f'error Detected2 ...: {e}')
                    raise Exception("Detected")

        print(f'Website title: {current_title}')

        if is_detected:
            cookie_filename = get_current_path2("saved_cookies/cookies_2.txt")
        else:
            cookie_filename = get_current_path2("saved_cookies/cookies_1.txt")

        with open(cookie_filename, 'r') as f:
            data = json.load(f)
        print(f'cookies data: {data}')

        cookie_str = ''
        for json_dict in data:
            for key, value in json_dict.items():
                print(f"key: {key} | value: {value}")
                if key == 'name':
                    cookie_str += value + '='
                if key == 'value':
                    cookie_str += value + ';'

        # remove last character: (;)
        new_cookie_str = cookie_str[:-1]
        print(new_cookie_str)

        encode_str = parse.quote(current_source, encoding='utf-8')
        return {
            "data": encode_str,
            "title": current_title,
            "navigator_user_agent": navigator_user_agent,
            "cookies": new_cookie_str
        }


    def get_new_driver(self, *args, **kwargs):
        """ This method overrides get_new_driver() from BaseCase. """
        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        options.add_experimental_option("useAutomationExtension", False)
        
        if self.headless:
            options.add_argument("--headless=new")  
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-extensions") 
        options.add_argument("--disable-gpu")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("start-maximized")  # act as real user
        # options.add_argument("--auto-open-devtools-for-tabs")  
        # options.add_argument("user-agent=Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0;  rv:11.0) like Gecko")
        
        # options.add_argument("--proxy-server=") # set proxy server

        service = webdriver.ChromeService('/usr/bin/chromedriver')
        return webdriver.Chrome(options=options, service=service)
        

    def solve(self, url=None, assert_element=None, user_agent=None, proxy=None) -> dict:
        # driver.get('https://arh.antoinevastel.com/bots/areyouheadless')  # check if you are chrome headless
        # driver.get('https://amiunique.org/fingerprint')  # check our browser fingerprint look unique
        # driver.get('https://bot.sannysoft.com')  # verify bot detected information

        print(f'request url: {url}')

        self.headless = True

        driver = self.get_new_driver()

        set_viewport_size2(driver=driver)
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
        )

        # go to the site page
        driver.execute_script(f"window.open(); window.location.href=\"{url}\"");
        # driver.get(url)        
        sleep(5)
        
        driver.save_screenshot(get_current_path('imgs/img1.png'))

        try:
            verify_success(driver=driver, assert_element=assert_element)
            current_title = driver.title
            current_source = driver.page_source
        except Exception as e:
            print('verify...')

            driver.save_screenshot(get_current_path('imgs/img2.png'))

            try:
                print('wait and switch to frame...')
                
                WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[title*='challenge']")))
                driver.save_screenshot(get_current_path('imgs/img3.png'))

                print('click...')
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
                driver.save_screenshot(get_current_path('imgs/img4.png'))

                sleep(10)
                driver.save_screenshot(get_current_path('imgs/img5.png'))

            except Exception as e:
                print(e)
                driver.save_screenshot(get_current_path('imgs/img5.png'))
                print('Timeout exception...')
                raise Exception('Detected')

            current_title = driver.title
            current_source = driver.page_source
            
        finally:
            # quit driver
            driver.quit()

        return {
            "title": current_title
        }
        
