import os
import pytest
import shared_driver


@pytest.fixture(scope="session", autouse=True)
def shared_session():
    """Session-scoped fixture that starts shared driver and logs in once for the whole pytest run."""
    headless = os.environ.get('HEADLESS', 'false').lower() in ('1', 'true', 'yes')
    shared_driver.start_driver(headless=headless)
    username = os.environ.get('TEST_USERNAME', 'alexsingh')
    password = os.environ.get('TEST_PASSWORD', 'demo123')
    shared_driver.login(username, password)

    yield

    # Teardown: logout and quit driver
    try:
        shared_driver.logout()
    finally:
        shared_driver.quit_driver()



def pytest_collection_modifyitems(items):
    """Run positive tests before negative tests. Unmarked default to positive."""
    def sort_key(item):
        is_neg = item.get_closest_marker("negative") is not None
        is_pos = item.get_closest_marker("positive") is not None
        priority = 0 if is_pos or not (is_pos or is_neg) else 1
        return (priority, item.fspath.basename.lower(), item.name.lower())
    items.sort(key=sort_key)
