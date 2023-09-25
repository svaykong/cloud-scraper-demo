import json
import platform
import os
from selenium import webdriver

sys = platform.system()


def set_json_data(data: dict) -> json:
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def get_current_path(file_path: str) -> str:
    if sys == 'Darwin':
        current_path = os.path.join(os.getcwd(), '../', file_path)
    else:
        current_path = os.path.join(os.getcwd(), '..\\', file_path)
    return current_path


def is_mac() -> bool:
    if sys == 'Darwin':
        return True
    else:
        return False


def screenshot(driver: webdriver, file_name: str) -> None:
    if is_mac():
        file = get_current_path(f'imgs/{file_name}')
    else:
        file = get_current_path(f'imgs\\{file_name}')
    driver.get_screenshot_as_file(file)
