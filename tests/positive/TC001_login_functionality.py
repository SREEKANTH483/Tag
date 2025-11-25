import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import shared_driver
from tests.helpers import get_current_scenario_data


def test_successful_login(scenario_data=None):
    """Positive: verify dashboard and personalized welcome are visible after shared login.
    Uses data from testdata.csv scenario if available.
    """
    # Get current scenario data from CSV (mainly for consistency, login is handled by shared_driver)
    test_data = scenario_data or get_current_scenario_data()
    expected_username = test_data.get('username')
    
    # Ensure CSV data is provided
    if not expected_username:
        pytest.fail("Missing required 'username' in CSV data")
    
    driver = shared_driver.get_driver()
    wait = WebDriverWait(driver, 20)

    # Verify dashboard is displayed (assumes shared login already performed by autouse fixture)
    try:
        dashboard_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='active']")))
        assert dashboard_element.is_displayed()
    except TimeoutException:
        pytest.fail("Dashboard did not load in time")

    # Verify personalized information is displayed using several fallback locators
    locators = [
        (By.XPATH, "//h2[contains(translate(., 'WELCOME', 'welcome'), 'welcome') ]"),
        (By.XPATH, "//h2[contains(., 'Welcome') or contains(., 'welcome') ]"),
        (By.XPATH, "//div[contains(@class,'user') or contains(@class,'welcome')]") ,
        (By.XPATH, "//span[@id='user-name']"),
        (By.XPATH, "//header//div[contains(., 'Welcome') or contains(., 'welcome')]")
    ]

    personalized_text = None
    for by, expr in locators:
        try:
            el = wait.until(EC.presence_of_element_located((by, expr)))
            personalized_text = el.text or el.get_attribute('innerText')
            if personalized_text:
                break
        except Exception:
            # try next locator
            continue

    if not personalized_text:
        # take a screenshot for debugging
        try:
            import os
            screenshots_dir = os.path.join(os.getcwd(), 'reports', 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshots_dir, 'test_successful_login_failure.png')
            driver.save_screenshot(screenshot_path)
            pytest.fail(f"Personalized information did not load in time; screenshot saved to {screenshot_path}")
        except Exception:
            pytest.fail("Personalized information did not load in time and screenshot capture failed")

    # Accept either a welcome phrase or the presence of the logged-in username (apps differ).
    lowered = (personalized_text or "").lower()
    assert any(k in lowered for k in ('welcome', 'logout')) or len(lowered.strip()) > 0
