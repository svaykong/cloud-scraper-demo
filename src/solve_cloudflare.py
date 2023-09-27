import random

from .common import get_current_path2
from urllib import parse
import json
from seleniumbase import SB, BaseCase
from selenium_stealth import stealth

BaseCase.main(__name__, __file__)


def verify_success(sb: SB, assert_element: str) -> None:
    sb.assert_element(assert_element, timeout=8)
    sb.sleep(4)


def set_viewport_size(sb: SB, width: int, height: int) -> None:
    window_size = sb.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, width, height)
    sb.set_window_size(*window_size)


class SolveCloudflare(BaseCase):
    def __init__(self):
        super().__init__()
        print('SolveCloudflare __init__')

    def solve(self, url=None, assert_element=None, agent=None) -> dict:
        print('Solve cloudflare...')

        # driver.get('https://arh.antoinevastel.com/bots/areyouheadless')  # check if you are chrome headless
        # driver.get('https://amiunique.org/fingerprint')  # check our browser fingerprint look unique
        # driver.get('https://bot.sannysoft.com')  # verify bot detected information

        print(f'request url: {url}')

        page_headers = ''
        current_title = ''
        current_source = ''
        navigator_user_agent = ''
        is_detected = False
        if agent == '':
            agent = None
        with SB(uc_cdp=True,
                incognito=True,
                headless="--headless",
                agent=agent,
                chromium_arg="""
                    --no-sandbox, 
                    --disable-setuid-sandbox,
                    --disable-extensions,
                    --disable-gpu,
                    --disable-dev-shm-usage,
                    start-maximized, 
                    --auto-open-devtools-for-tabs
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

            random_width = 1920 + random.randint(0, 100)  # 800, 1920
            random_height = 3000 + random.randint(0, 100)  # 600, 3000
            set_viewport_size(sb, random_width, random_height)

            sb.open(url)

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
                    verify_success(sb=sb, assert_element=assert_element)
                except Exception as e:
                    print(f'error Detected2 ...: {e}')
                    raise Exception("Detected")

        print(f'Website title: {current_title}')
        print(f'Website header: {page_headers}')

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
        return {"data": encode_str, "title": current_title, "navigator_user_agent": navigator_user_agent,
                "cookies": new_cookie_str}
