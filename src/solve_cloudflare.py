from sas_driver import SASDriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib import parse
from common import screenshot


class SolveCloudflare:
    def __init__(self):
        print('SolveCloudflare __init__')
        pass

    @staticmethod
    def solve(url=None, user_agent=None, use_random_agent=False, random_agent_name=None) -> dict:
        print('Solve cloudflare...')

        sas_driver = SASDriver()
        if user_agent is not None and user_agent != '':
            sas_driver.userAgent = user_agent

        if use_random_agent:
            if random_agent_name is not None and random_agent_name != '':
                sas_driver.randomAgentName = random_agent_name
                sas_driver.set_random_user_agent()

        sas_driver.init_chrome_option()
        sas_driver.init_driver()
        driver = sas_driver.driver

        # driver.get('https://arh.antoinevastel.com/bots/areyouheadless')  # check if you are chrome headless
        # driver.get('https://amiunique.org/fingerprint')  # check our browser fingerprint look unique
        # driver.get('https://bot.sannysoft.com')  # verify bot detected information

        print(f'request url: {url}')

        # driver.get(url)
        driver.execute_script('''window.open("http://nowsecure.nl","_blank");''')  # open page in new tab
        sleep(5)  # wait until page has loaded
        driver.switch_to.window(window_name=driver.window_handles[0])  # switch to first tab
        driver.close()  # close first tab
        driver.switch_to.window(window_name=driver.window_handles[0])  # switch back to new tab
        sleep(2)
        driver.get("https://google.com")
        sleep(2)
        driver.get("https://nowsecure.nl")  # this should pass cloudflare captchas now

        sleep(5)  # Wait for the page to load

        print(f'title: {driver.title}')  # obtains title

        result_str = driver.page_source
        is_chk = False
        bypass_success = False
        error = ""

        # verify is there is a cloudflare exist.
        if result_str.find('needs to review the security of your connection before proceeding') > -1:
            is_chk = True
        else:
            bypass_success = True

        if is_chk:
            try:
                print("waiting for iframe finished loading and switch to it...")

                screenshot(driver=driver, file_name="waiting_frame.png")

                # Wait for the CAPTCHA to load
                WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))
                # WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))

                # click the checkbox label
                print("wait and try to click checkbox")
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()

                screenshot(driver=driver, file_name='click_checkbox.png')

                sleep(20)  # Wait for the page after click
                print(f'title update: {driver.title}')  # obtains title update

                screenshot(driver=driver, file_name="after_click.png")

                bypass_success = True
            except (TimeoutException, Exception) as e:
                if e is Exception:
                    print(f'exception: {e}')
                    error = e
                else:
                    print('Timeout exception...')
                    error = 'Timeout exception'

                bypass_success = False

        title = driver.title
        driver.quit()

        if bypass_success:
            msg = "success"
        else:
            msg = "failed"

        encode_str = parse.quote(result_str, encoding='utf-8')
        return {"data": encode_str, "title": title, "bypass": msg, "error": error}
