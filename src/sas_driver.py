# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import yaml
import random
import os

default_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                'Chrome/99.0.9999.999 Safari/537.36'


class SASDriver:
    def __init__(self, user_agent=default_agent, use_random_user_agent=False, random_agent='Firefox'):
        print('SASDriver __init__')
        self.isDriverNone = True
        self.user_agent = user_agent
        self.use_random_user_agent = use_random_user_agent
        self.random_agent = random_agent
        self.driver = None
        self.chrome_options = None

    def init_chrome_option(self):
        print('init chrome option start.')

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("start-maximized")  # act as real user
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)
        self.chrome_options.add_argument("--disable-extensions")  # disable chrome extensions
        self.chrome_options.add_argument("--disable-gpu")  # Temporarily needed if running on Windows.
        self.chrome_options.add_argument("--no-sandbox")  # linux only

        '''
            The following work all for headless mode
            
            # for Chrome >= 109
            self.chrome_options.add_argument("--headless=new")  
            self.chrome_options.add_argument("--headless")
            self.chrome_options.headless = True
        '''
        self.chrome_options.headless = False
        self.chrome_options.add_experimental_option("detach", True)  # Make selenium browser to stay open

        if self.use_random_user_agent:
            # setting headers
            current_path = os.path.join(os.getcwd() + "..\\..\\", "user_agents.yml")
            print(f'current path: {current_path}')
            with open(current_path) as f_agent:
                uagent = yaml.safe_load(f_agent)

            ie = self.random_agent
            print(f'ie: {ie}')

            count = 16  # Firefox
            if ie == 'Chrome':
                count = 7
            elif ie == 'Edge':
                count = 4
            elif ie == 'IE':
                count = 2
            elif ie == 'Other':
                count = 4

            random_number = random.randint(0, count)
            print(f'random number: {random_number}')

            if ie != 'Chrome' and ie != 'Firefox' and ie != 'IE' and ie != 'Edge' and ie != 'Other':
                raise Exception('Invalid agent.')

            random_agent = uagent[ie][random_number]
            print(f'random agent: {random_agent}')

            # set random user-agent
            # self.chrome_options.add_argument(f"user-agent={random_agent}")
        else:
            if self.user_agent is None:
                self.user_agent = ''
            if self.user_agent == '':
                self.user_agent = default_agent

            print(f'self.user_agent: {self.user_agent}')

            self.chrome_options.add_argument(f"--user-agent={self.user_agent}")

        # self.chrome_options.add_argument("force-device-scale-factor=1")  # set deviceScaleFactor: 1 or 0.75
        # self.chrome_options.add_argument("high-dpi-support=1")  # set highDpiSupport: 1 or 0.75
        # self.chrome_options.add_argument("has-touch=false")  # set hasTouch: false
        # self.chrome_options.add_argument("is-lanscape=false")  # set isLanscape: false
        # self.chrome_options.add_argument("is-mobile=false")  # set isMobile: false

        print('init chrome option end.')

    def init_driver(self):
        print('init driver start.')

        if self.chrome_options is None:
            raise Exception('Chrome Option is not initialize')

        self.driver = webdriver.Chrome(options=self.chrome_options)

        random_width = 1920 + random.randint(0, 100)  # 800, 1920
        random_height = 3000 + random.randint(0, 100)  # 600, 3000

        self.__set_viewport_size(random_width, random_height)  # set the viewport size to random: (width x height)

        # display the viewport size
        print(f'viewport size: {self.driver.execute_script("return [window.innerWidth, window.innerHeight];")}')

        self.isDriverNone = False
        print('init driver end.')

    def __set_viewport_size(self, width, height):
        if self.chrome_options is not None:
            window_size = self.driver.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, width, height)
            self.driver.set_window_size(*window_size)

    def add_argument(self, value):
        print(f'argument value: {value}')

        if self.chrome_options is not None and self.isDriverNone:
            self.chrome_options.add_argument(value)

    def add_experimental_option(self, value):
        print(f'experimental_option value: {value}')

        if self.chrome_options is not None and self.isDriverNone:
            self.chrome_options.add_experimental_option(value)
