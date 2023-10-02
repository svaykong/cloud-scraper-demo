import random

from .common import get_current_path2
from urllib import parse
import json
from seleniumbase import SB


def verify_success(sb: SB, assert_element: str) -> None:
    sb.assert_element(assert_element, timeout=8)
    sb.sleep(4)


def set_viewport_size(sb: SB, width: int, height: int) -> None:
    window_size = sb.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, width, height)
    sb.set_window_size(*window_size)


class SolveCloudflare:
    def __init__(self):
        print('SolveCloudflare __init__')

    def solve(self, url=None, assert_element=None, proxy=None) -> dict:
        print('Solve cloudflare...')

        # driver.get('https://arh.antoinevastel.com/bots/areyouheadless')  # check if you are chrome headless
        # driver.get('https://amiunique.org/fingerprint')  # check our browser fingerprint look unique
        # driver.get('https://bot.sannysoft.com')  # verify bot detected information

        print(f'request url: {url}')

        is_detected = False
        with SB(
                uc_cdp=True,
                incognito=True,
                agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
                proxy=proxy,
                headless="--headless",
                chromium_arg='--start-maximized, --no-sandbox,' +
                             '--disable-extensions, --disable-gpu,' +
                             '--disable-dev-shm-usage',
                ) as sb:

            random_width = 1920 + random.randint(0, 100)
            random_height = 3000 + random.randint(0, 100)
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
                sb.save_screenshot(name="verify.png")
                is_detected = True
                if sb.is_element_visible('input[value*="Verify"]'):
                    sb.slow_click('input[value*="Verify"]')
                elif sb.is_element_visible('iframe[title*="challenge"]'):
                    sb.switch_to_frame('iframe[title*="challenge"]')
                    sb.slow_click("span.mark")
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
