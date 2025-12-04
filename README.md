# Regression Test Suite

Data-driven Selenium test suite with flexible scenario selection. Tests healthcare application functionality including login, cost estimation, claim submission, and provider search.

## Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run Tests

**Run all scenarios:**
```powershell
python run_scenarios_selective.py
```

**Run specific scenarios:**
```powershell
# First 3 scenarios
python run_scenarios_selective.py --first 3

# Last 2 scenarios  
python run_scenarios_selective.py --last 2

# Specific scenarios
python run_scenarios_selective.py --scenarios 1,3,5

# Scenario range
python run_scenarios_selective.py --range 2-4
```

**Run single scenario (first row only):**
```powershell
python run_unittest_regression.py
```

### 3. View Results
- HTML reports are generated in `reports/` folder
- Open `reports/index.html` to see all reports

## Test Data Configuration

Edit `testdata/testdata.csv` to modify test scenarios. Each row represents a complete test scenario with data for all test cases.

**CSV Structure:**
```csv
scenario_name,username,password,estimate_cpt,estimate_location,claim_cpt,claim_location,provider_specialty,...
Scenario_1,alexsingh,demo123,99213,Clinic,87070,Hospital,Primary Care,...
```

## Environment Options

**Headless Mode:**
```powershell
python run_scenarios_selective.py --headless
```

**Environment Variables:**
- `TEST_USERNAME` — login username (default: from CSV)
- `TEST_PASSWORD` — login password (default: from CSV)  
- `HEADLESS` — run headless when set to `1`, `true`, or `yes`

## Key Features

- **Data-driven**: All test data comes from `testdata.csv`
- **No fallback defaults**: Tests fail if CSV data is missing
- **Flexible selection**: Run specific scenarios or ranges
- **Single browser session**: Efficient login once per scenario
- **Individual reports**: Separate HTML report per scenario
## File Structure

```
├── testdata/
│   └── testdata.csv              # Test scenario data
├── tests/
│   ├── positive/                 # Positive test cases
│   ├── negative/                 # Negative test cases  
│   └── helpers.py               # Test utilities
├── reports/                     # Generated HTML reports
├── run_scenarios_selective.py   # Main test runner
├── run_unittest_regression.py   # Single scenario runner
├── shared_driver.py            # WebDriver management
├── conftest.py                 # Pytest configuration
└── requirements.txt            # Dependencies
```

## Requirements

- Python 3.8+
- Chrome browser
- Internet connection (for test website)

For detailed usage examples, see `SCENARIO_SELECTION_GUIDE.md`
