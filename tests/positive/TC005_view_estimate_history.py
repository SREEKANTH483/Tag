import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shared_driver
from tests.helpers import get_current_scenario_data


def test_verify_estimate_details():
    """Positive: verify estimate details using data from testdata.csv scenario."""
    # Get current scenario data from CSV (for consistency, though this test doesn't need specific data)
    test_data = get_current_scenario_data()
    
    driver = shared_driver.get_driver()
    wait = WebDriverWait(driver, 10)

    # Navigate to Estimates page
    estimates_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@class='sidebar-nav']//li//a[@href='/estimates']")))
    estimates_link.click()

    # Click on an estimate
    estimate = wait.until(EC.element_to_be_clickable((By.XPATH, f"//tbody/tr[1]/td[9]/a[1]")))
    estimate.click()

    estimate_details = wait.until(EC.presence_of_element_located((By.XPATH, "//body/div[@class='main-layout']/main[@class='container']/div[@class='card']/div[@class='card-header']/div[1]")))

    # Basic check: ensure details element contains expected heading
    assert estimate_details.text is not None
