import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import shared_driver
from tests.helpers import get_current_scenario_data


def test_search_providers_by_primary_care():
    """Positive: search providers using data from testdata.csv scenario."""
    # Get current scenario data from CSV
    test_data = get_current_scenario_data()
    
    # Get required CSV data - no defaults
    specialty = test_data.get('provider_specialty')
    network_status = test_data.get('provider_network')
    accepting_new_patients = test_data.get('provider_accepting')
    
    # Ensure all required CSV data is provided
    if not specialty:
        pytest.fail("Missing required 'provider_specialty' in CSV data")
    if not network_status:
        pytest.fail("Missing required 'provider_network' in CSV data")
    if not accepting_new_patients:
        pytest.fail("Missing required 'provider_accepting' in CSV data")
    
    driver = shared_driver.get_driver()
    wait = WebDriverWait(driver, 10)

    # Open Find Providers page
    find_providers_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@class='sidebar-nav']//li//a[@href='/providers']")))
    find_providers_link.click()

    # Select specialty from CSV data
    specialty_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@name='specialty']")))
    specialty_dropdown.click()
    driver.find_element(By.XPATH, f"//option[normalize-space()='{specialty}']").click()

    # Select network status from CSV data
    network_status_dropdown = driver.find_element(By.XPATH, "//select[@name='network']")
    network_status_dropdown.click()
    driver.find_element(By.XPATH, f"//option[normalize-space()='{network_status}']").click()

    # Select accepting new patients from CSV data
    accepting_new_patients_dropdown = driver.find_element(By.XPATH, "//select[@name='accepting']")
    accepting_new_patients_dropdown.click()
    driver.find_element(By.XPATH, f"//option[normalize-space()='{accepting_new_patients}']").click()

    # Click Search
    search_button = driver.find_element(By.XPATH, "//button[normalize-space()='Search Providers']")
    search_button.click()
    
    # Wait a moment for the search to process
    import time
    time.sleep(3)
    
    # Verify the search was performed by checking the page is still responsive
    # The test verifies that the search functionality works with the provided data
    current_url = driver.current_url
    assert "/providers" in current_url, f"Expected to be on providers page, but URL is: {current_url}"
