import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import shared_driver
from tests.helpers import get_current_scenario_data

@pytest.mark.negative
def test_invalid_cpt_code_shows_error_banner():
    """Negative: test invalid CPT code using data from testdata.csv scenario."""
    # Get current scenario data from CSV
    test_data = get_current_scenario_data()
    
    # Get required CSV data - no defaults
    invalid_cpt = test_data.get('invalid_cpt')
    service_location = test_data.get('estimate_location')
    network_status = test_data.get('estimate_network')
    
    # Ensure all required CSV data is provided
    if not invalid_cpt:
        pytest.fail("Missing required 'invalid_cpt' in CSV data")
    if not service_location:
        pytest.fail("Missing required 'estimate_location' in CSV data")
    if not network_status:
        pytest.fail("Missing required 'estimate_network' in CSV data")
    
    driver = shared_driver.get_driver()
    wait = WebDriverWait(driver, 15)

    # Navigate to Estimate page (try safe locator first, then fallback)
    try:
        link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/estimate']")))
    except TimeoutException:
        link = wait.until(EC.element_to_be_clickable((By.XPATH, "(//a[@href='/estimate'])[2]")))

    try:
        driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", link)
    except Exception:
        pass
    link.click()

    # Enter invalid CPT from CSV data
    cpt_input = wait.until(EC.visibility_of_element_located((By.NAME, "cpt")))
    cpt_input.clear()
    cpt_input.send_keys(invalid_cpt)

    # Select location from CSV data
    wait.until(EC.element_to_be_clickable((By.ID, "est_site"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, f"//option[normalize-space()='{service_location}']"))).click()

    # Select network from CSV data
    if 'In-Network' in network_status:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='est_inn_true']"))).click()
    else:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='est_inn_false']"))).click()

    # Calculate
    wait.until(EC.element_to_be_clickable((By.ID, "est_submit"))).click()

    # Validate error message
    msg = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'alert') and contains(@class,'error')]")))
    text = msg.text.strip().lower()
    assert any(k in text for k in ["invalid", "not recognized", "unknown"]), f"Unexpected error text: {msg.text}"
