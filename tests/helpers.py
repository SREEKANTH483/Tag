"""Common test helpers used by pytest tests in this project.

Keep helpers small and UI-agnostic; prefer to add selectors in page-specific modules if needed.
"""
import csv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_element(driver, locator, timeout=15):
    """Wait for an element to be present and return it; raise on timeout."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located(locator))


def click_when_clickable(driver, locator, timeout=15):
    wait = WebDriverWait(driver, timeout)
    el = wait.until(EC.element_to_be_clickable(locator))
    el.click()
    return el


def get_text_safe(element):
    if element is None:
        return ""
    return (element.text or element.get_attribute('innerText') or "").strip()


def load_test_data(scenario_filter=None):
    """Load test data from testdata.csv file.
    
    Args:
        scenario_filter: Optional string to filter by scenario_name column
        
    Returns:
        List of dictionaries containing test data rows
    """
    # Get the project root directory (parent of tests directory)
    current_dir = os.path.dirname(__file__)  # tests directory
    project_root = os.path.dirname(current_dir)  # project root
    csv_path = os.path.join(project_root, 'testdata', 'testdata.csv')
    test_data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                    
                # Filter by scenario if specified
                if scenario_filter and row.get('scenario_name', '').strip() != scenario_filter:
                    continue
                    
                # Clean up empty string values
                cleaned_row = {}
                for key, value in row.items():
                    cleaned_row[key] = value.strip() if value else ''
                    
                test_data.append(cleaned_row)
                
    except FileNotFoundError:
        print(f"Warning: testdata.csv not found at {csv_path}")
        return []
    except Exception as e:
        print(f"Error reading testdata.csv: {e}")
        return []
        
    return test_data


def get_current_scenario_data():
    """Get the current scenario data. 
    
    Returns:
        Dictionary with test data or empty dict if not found
    """
    # Check if we're running a specific scenario via environment variable
    scenario_index = os.environ.get('CURRENT_SCENARIO')
    if scenario_index:
        try:
            data = load_test_data()
            index = int(scenario_index) - 1  # Convert to 0-based index
            if 0 <= index < len(data):
                return data[index]
        except (ValueError, IndexError):
            pass
    
    # Try to get from parametrized conftest first
    try:
        from conftest_parametrized import get_current_scenario_data as get_param_data
        result = get_param_data()
        # If parametrized conftest returns empty, use fallback
        if result:
            return result
    except ImportError:
        pass
    
    # Fallback to first scenario for non-parametrized runs
    data = load_test_data()
    return data[0] if data else {}


def get_test_data_for_case(testcase):
    """Backward compatibility function - now gets current scenario data.
    
    Args:
        testcase: The testcase identifier (ignored in new structure)
        
    Returns:
        Dictionary with test data or empty dict if not found
    """
    return get_current_scenario_data()
