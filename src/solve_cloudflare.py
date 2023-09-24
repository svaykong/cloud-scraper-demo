from sas_driver import SASDriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SolveCloudflare:
    def __init__(self):
        print('SolveCloudflare __init__')
        pass

    @staticmethod
    def solve(url, user_agent=None, use_random_user_agent=False, random_agent='Firefox') -> dict:
        print('Solve cloudflare...')

        sas_driver = SASDriver(user_agent=user_agent,
                               use_random_user_agent=use_random_user_agent,
                               random_agent=random_agent)
        sas_driver.init_chrome_option()
        sas_driver.init_driver()
        driver = sas_driver.driver

        # driver.get('https://arh.antoinevastel.com/bots/areyouheadless')  # check if you are chrome headless
        # driver.get('https://amiunique.org/fingerprint')  # check our browser fingerprint look unique
        # driver.get('https://bot.sannysoft.com')  # verify bot detected information

        print(f'request url: {url}')

        driver.get(url)

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
                # Wait for the CAPTCHA to load
                WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))
                # WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))

                # click the checkbox label
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()

            except (TimeoutException, Exception) as e:
                print(f'exception: {e}')
                error = e
                bypass_success = False

        if is_chk and bypass_success:
            sleep(10)  # Wait for the page to load
            print(f'title update: {driver.title}')  # obtains title update

            result_str = driver.page_source
            print(result_str)  # obtains the contents update

        driver.quit()

        return {"data": result_str, "status": bypass_success, "error": error}
