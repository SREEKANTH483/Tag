import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shared_driver
from tests.helpers import get_current_scenario_data


def test_view_claims_page():
    """Positive: view claims page using data from testdata.csv scenario."""
    # Get current scenario data from CSV (for consistency, though this test doesn't need specific data)
    test_data = get_current_scenario_data()
    
    driver = shared_driver.get_driver()
    wait = WebDriverWait(driver, 10)

    claims_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@class='sidebar-nav']//li//a[@href='/claims']")))
    claims_link.click()

    # Verify claims table exists and has rows
    wait.until(EC.presence_of_element_located((By.XPATH, "//table[.//th[normalize-space()='Claim #']]")))
    rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[.//th[normalize-space()='Claim #']]//tbody/tr")))
    assert len(rows) > 0
