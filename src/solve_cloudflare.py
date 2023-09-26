from .common import get_current_path2
from urllib import parse
import json
from seleniumbase import SB, BaseCase

BaseCase.main(__name__, __file__)


def verify_success(sb: SB, assert_element: str) -> None:
    sb.assert_element(assert_element, timeout=8)
    sb.sleep(4)


class SolveCloudflare(BaseCase):
    def __init__(self):
        super().__init__()
        print('SolveCloudflare __init__')

    def solve(self, url=None, assert_element=None) -> dict:
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
        with SB(uc_cdp=True, incognito=True, headless="--headless", agent="python-requests/2.31.0") as sb:
            sb.open(url)
            try:
                verify_success(sb=sb, assert_element=assert_element)
                current_title = sb.get_title()
                current_source = sb.get_page_source()
                navigator_user_agent = sb.get_user_agent()
                sb.save_cookies(name="cookies_1.txt")

                # _xhr.getAllResponseHeaders().trim().split( / [\\r\\n]+ /).map((value) = > value.split( /: / )).forEach(
                #     (keyValue) = > {
                #     _headers[keyValue[0].trim()] = keyValue[1].trim();
                # });
                # js_headers = '''
                #     const _xhr = new XMLHttpRequest();
                #     _xhr.open("HEAD", document.location, false);
                #     _xhr.send(null);
                #
                #     const _headers = {};
                #
                #     _xhr.requestHeaders().trim().split(/[\\r\\n]+/).map((value) => value.split(/: /)).forEach((keyValue) => {
                #         _headers[keyValue[0].trim()] = keyValue[1].trim();
                #     });
                #
                #     return _headers;
                # '''
                # page_headers = sb.execute_script(js_headers)
            except Exception as e:
                print(f'{e} verify ...')
                is_detected = True
                if sb.is_element_visible('input[value*="Verify"]'):
                    sb.click('input[value*="Verify"]')
                elif sb.is_element_visible('iframe[title*="challenge"]'):
                    sb.switch_to_frame('iframe[title*="challenge"]')
                    sb.click("span.mark")
                else:
                    raise Exception("Detected!")
                try:
                    verify_success(sb=sb, assert_element=assert_element)
                    current_title = sb.get_title()
                    current_source = sb.get_page_source()
                    navigator_user_agent = sb.get_user_agent()
                    sb.save_cookies(name="cookies_2.txt")
                except Exception:
                    raise Exception("Detected!")

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
