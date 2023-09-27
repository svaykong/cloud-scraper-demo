import random

from selenium_stealth import stealth

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
    def solve(self, url=None, assert_element=None, agent=None) -> dict:
        print('Solve cloudflare...')

        with SB(browser="chrome",
                incognito=True,
                headless="--headless",
                chromium_arg="""
                    --no-sandbox,
                    --disable-setuid-sandbox,
                    --disable-extensions,
                    --disable-gpu,
                    --disable-dev-shm-usage,
                """,
                ) as sb:

            # stealth(
            #     sb.driver,
            #     languages=["en-US", "en"],
            #     vendor="Google Inc.",
            #     platform="Win32",
            #     webgl_vendor="Intel Inc.",
            #     renderer="Intel Iris OpenGL Engine",
            #     run_on_insecure_origins=True
            # )

            random_width = 1920 + random.randint(0, 100)  # 800, 1920
            random_height = 3000 + random.randint(0, 100)  # 600, 3000
            # set_viewport_size(sb, random_width, random_height)

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
            return {"data": encode_str,
                    "title": current_title,
                    "navigator_user_agent": navigator_user_agent,
                    "cookies": cookies}
