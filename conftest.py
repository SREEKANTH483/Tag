import os
import pytest
import shared_driver
from _pytest.runner import TestReport


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


def pytest_runtest_makereport(item, call):
    """Hook to run negative scenarios after a test fails."""
    if call.when == "call":
        report = TestReport.from_item_and_call(item, call)
        if report.failed:
            # Check if a corresponding negative test exists
            negative_test_name = f"negative/{item.name}"
            negative_test_path = os.path.join(os.path.dirname(item.fspath), negative_test_name + ".py")

            if os.path.exists(negative_test_path):
                # Dynamically add the negative test to the test queue
                item.session.items.append(pytest.Function.from_parent(
                    parent=item.parent, name=negative_test_name
                ))
