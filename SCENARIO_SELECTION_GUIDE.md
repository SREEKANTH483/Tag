# Scenario Selection Guide

This guide explains how to run specific test scenarios from your `testdata.csv` file.

## Available Commands

### 1. Run All Scenarios (Default)
```powershell
python run_scenarios_selective.py
```
Runs all scenarios in the CSV file.

### 2. Run First N Scenarios
```powershell
python run_scenarios_selective.py --first 5
```
Runs the first 5 scenarios from the CSV.

### 3. Run Last N Scenarios  
```powershell
python run_scenarios_selective.py --last 3
```
Runs the last 3 scenarios from the CSV.

### 4. Run Scenario Range
```powershell
python run_scenarios_selective.py --range 2-5
```
Runs scenarios 2, 3, 4, and 5 from the CSV.

### 5. Run Specific Scenarios
```powershell
python run_scenarios_selective.py --scenarios 1,3,7,10
```
Runs only scenarios 1, 3, 7, and 10 from the CSV.

## Additional Options

### Headless Mode
Add `--headless` to run tests without opening browser windows:
```powershell
python run_scenarios_selective.py --first 3 --headless
```

### Verbose Output
Add `--verbose` or `-v` for detailed output:
```powershell
python run_scenarios_selective.py --last 2 --verbose
```

## Windows Batch File
You can also use the batch file:
```cmd
run_selective.bat --first 5
run_selective.bat --scenarios 1,3,7
```

## Examples with Your Current CSV

With your 7 scenarios (Scenario_1 through Scenario_7):

```powershell
# Test only the first scenario (known to pass)
python run_scenarios_selective.py --first 1

# Test scenarios 1 and 4 specifically  
python run_scenarios_selective.py --scenarios 1,4

# Test the last 2 scenarios
python run_scenarios_selective.py --last 2

# Test a range of scenarios
python run_scenarios_selective.py --range 3-5

# Run all scenarios in headless mode
python run_scenarios_selective.py --headless
```

## Output Reports

Each scenario generates its own HTML report:
- `reports/scenario_1_Scenario_1_TIMESTAMP.html`
- `reports/scenario_4_Scenario_4_TIMESTAMP.html`
- etc.

## Error Handling

- Invalid ranges: `--range 10-15` (when you only have 7 scenarios)
- Invalid scenarios: `--scenarios 1,15,20` (scenarios 15,20 don't exist)
- Invalid format: `--range 2,5` (should be `2-5`)

The script will show warnings and skip invalid scenarios.

## Performance Tips

- Use `--first 1` to quickly test if your setup works
- Use `--scenarios` to test specific problematic scenarios
- Use `--headless` for faster execution in CI/automation
- Use `--range` for testing consecutive scenarios efficiently