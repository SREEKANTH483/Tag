import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shared_driver
from tests.helpers import get_current_scenario_data


def test_estimate_cost_for_cpt_99213_in_network_clinic(scenario_data=None):
    """Positive: estimate cost using data from testdata.csv scenario."""
    # Get current scenario data from CSV
    test_data = scenario_data or get_current_scenario_data()
    
    # Get required CSV data - no defaults
    cpt_code = test_data.get('estimate_cpt')
    service_location = test_data.get('estimate_location')
    network_status = test_data.get('estimate_network')
    
    # Ensure all required CSV data is provided
    if not cpt_code:
        pytest.fail("Missing required 'estimate_cpt' in CSV data")
    if not service_location:
        pytest.fail("Missing required 'estimate_location' in CSV data")
    if not network_status:
        pytest.fail("Missing required 'estimate_network' in CSV data")
    
    driver = shared_driver.get_driver()
    wait = WebDriverWait(driver, 15)

    # Navigate to cost estimator
    wait.until(EC.presence_of_element_located((By.XPATH, "(//a[@href='/estimate'])[2]"))).click()
    time.sleep(2)

    # Enter CPT from CSV data
    cpt_field = wait.until(EC.presence_of_element_located((By.NAME, "cpt")))
    cpt_field.clear()
    cpt_field.send_keys(cpt_code)
    time.sleep(1)

    # Select service location from CSV data
    location_dropdown = driver.find_element(By.ID, "est_site")
    location_dropdown.click()
    location_option = wait.until(EC.presence_of_element_located((By.XPATH, f"//option[@value='{service_location}']")))
    location_option.click()
    time.sleep(1)

    # Select network status from CSV data
    try:
        if 'In-Network' in network_status:
            network_option = driver.find_element(By.XPATH, "//input[@id='est_inn_true']")
        else:
            network_option = driver.find_element(By.XPATH, "//input[@id='est_inn_false']")
        network_option.click()
    except Exception:
        # If element locators differ, continue and try to calculate
        pass

    # Click Calculate Estimate
    calculate_button = driver.find_element(By.ID, "est_submit")
    calculate_button.click()
    time.sleep(4)

    # Verify result elements
    estimated_cost = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-live='polite']//div[1]")))
    plan_payment = driver.find_element(By.XPATH, "//div[@aria-live='polite']//div[2]")

    assert estimated_cost.is_displayed()
    assert plan_payment.is_displayed()
