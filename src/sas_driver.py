from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import yaml
import random
from typing import Union
from common import get_current_path

defaultAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
               'Chrome/99.0.9999.999 Safari/537.36'


class SASDriver:

    def __init__(self):
        print('SASDriver __init__')
        self.isDriverNone = True
        self.userAgent = ''
        self.isDefaultAgent = False
        self.isRandomAgent = False
        self.randomAgentName = 'Firefox'
        self.driver = None
        self.chromeOptions = None

    def init_chrome_option(self) -> None:
        print('init chrome option start.')

        self.chromeOptions = Options()
        self.add_argument("start-maximized")  # act as real user
        self.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.add_experimental_option("useAutomationExtension", False)
        self.add_argument("--disable-extensions")  # disable chrome extensions
        # self.add_argument("--disable-gpu")  # Temporarily needed if running on Windows.
        # self.add_argument("--no-sandbox")  # linux only
        self.add_argument("--auto-open-devtools-for-tabs")  # automatically open dev tools on every new tab

        '''
            The following work all for headless mode
            
            # for Chrome >= 109
            self.add_argument("--headless=new")  
            self.add_argument("--headless")
            self.headless = True
        '''
        self.add_argument("--headless")
        # self.add_experimental_option("detach", True)  # Make selenium browser to stay open

        if self.userAgent != '':
            self.add_argument(f"--user-agent={self.userAgent}")

        if self.isDefaultAgent:
            self.add_argument(f"--user-agent={defaultAgent}")

        if self.isRandomAgent:
            self.set_random_user_agent()

        print('init chrome option end.')

    def init_driver(self) -> None:
        print('init driver start.')

        if self.chromeOptions is None:
            raise Exception('Chrome Option is not initialize')

        self.driver = webdriver.Chrome(options=self.chromeOptions)

        # add stealth here...
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine"
        )

        random_width = 1920 + random.randint(0, 100)  # 800, 1920
        random_height = 3000 + random.randint(0, 100)  # 600, 3000

        # set the viewport size to random: (width x height)
        self.__set_viewport_size(random_width, random_height)

        # display the viewport size
        print(f'viewport size: {self.driver.execute_script("return [window.innerWidth, window.innerHeight];")}')

        self.isDriverNone = False
        print('init driver end.')

    def __set_viewport_size(self, width: int, height: int) -> None:
        if self.chromeOptions is not None:
            window_size = self.driver.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
            window.outerHeight - window.innerHeight + arguments[1]];
            """, width, height)
            self.driver.set_window_size(*window_size)

    def add_argument(self, value: str) -> None:
        print(f'add argument value: {value}')
        self.chromeOptions.add_argument(value)

    def add_experimental_option(self, name: str, value: Union[str, int, dict, list[str]]) -> None:
        print(f'add experimental option name: {name}')
        print(f'add experimental option value: {value}')
        self.chromeOptions.add_experimental_option(name=name, value=value)

    def set_random_user_agent(self) -> None:
        current_path = get_current_path('user_agents.yml')
        with open(current_path) as f_agent:
            uagent = yaml.safe_load(f_agent)
        random_number = random.randint(0, 16)
        print(f'random number: {random_number}')

        ua_name = self.randomAgentName
        if (ua_name != 'Chrome' and
                ua_name != 'Firefox' and
                ua_name != 'Edge' and
                ua_name != 'IE' and
                ua_name != 'Other'):
            raise Exception('Invalid agent.')

        random_agent = uagent[ua_name][random_number]
        print(f'random agent: {random_agent}')

        self.userAgent = random_agent
        self.add_argument(f"--user-agent={self.userAgent}")
