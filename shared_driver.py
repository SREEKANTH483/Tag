from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

_driver = None
_wait = None
_login_url = "http://ec2-13-203-252-128.ap-south-1.compute.amazonaws.com:32794/login"

def start_driver(headless=False):
    global _driver, _wait
    if _driver is None:
        options = webdriver.ChromeOptions()
        # If headless not explicitly provided, read from env var HEADLESS
        if headless is False:
            headless_env = os.environ.get('HEADLESS', 'false').lower()
            headless = headless_env in ('1', 'true', 'yes')
        if headless:
            # Use new headless mode when available; fall back to legacy where needed
            try:
                options.add_argument('--headless=new')
            except Exception:
                options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        _driver = webdriver.Chrome(options=options)
        _driver.maximize_window()
        _driver.implicitly_wait(10)
        _wait = WebDriverWait(_driver, 15)
    return _driver

def get_driver():
    if _driver is None:
        return start_driver()
    return _driver

def get_wait():
    return _wait

def login(username: str = None, password: str = None):
    """Perform a login using the shared driver. Username/password default to env vars TEST_USERNAME/TEST_PASSWORD."""
    if username is None:
        username = os.environ.get('TEST_USERNAME', 'alexsingh')
    if password is None:
        password = os.environ.get('TEST_PASSWORD', 'demo123')
    d = get_driver()
    w = get_wait()
    d.get(_login_url)
    username_field = w.until(EC.presence_of_element_located((By.ID, "username")))
    password_field = d.find_element(By.ID, "password")
    username_field.clear()
    username_field.send_keys(username)
    password_field.clear()
    password_field.send_keys(password)
    # click sign in (tries several possible buttons)
    try:
        d.find_element(By.XPATH, '//button[normalize-space()="Sign In"]').click()
    except Exception:
        try:
            d.find_element(By.XPATH, "//button[@type='submit']").click()
        except Exception:
            d.find_element(By.XPATH, "//button").click()
    # small wait for dashboard
    time.sleep(2)
    return True

def logout():
    d = get_driver()
    w = get_wait()
    try:
        btn = w.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Logout') or normalize-space()='Logout']")))
        btn.click()
        w.until(EC.presence_of_element_located((By.ID, "username")))
    except Exception:
        # best-effort logout; ignore failures
        pass

def quit_driver():
    global _driver, _wait
    if _driver is not None:
        try:
            _driver.quit()
        except Exception:
            pass
    _driver = None
    _wait = None
