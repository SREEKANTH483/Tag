#!/usr/bin/env python3
"""
Selective Scenario Runner - Run specific scenarios from testdata.csv

This script allows you to run:
- First N scenarios: --first 5
- Last N scenarios: --last 3  
- Specific range: --range 2-5
- Specific scenarios: --scenarios 1,3,7
- All scenarios: (no arguments)

Usage Examples:
    python run_scenarios_selective.py --first 5
    python run_scenarios_selective.py --last 3
    python run_scenarios_selective.py --range 2-5
    python run_scenarios_selective.py --scenarios 1,3,7,10
    python run_scenarios_selective.py  # Run all
"""
import os
import sys
import subprocess
import argparse
from datetime import datetime
import shutil
from tests.helpers import load_test_data

def parse_arguments():
    """Parse command line arguments for scenario selection."""
    parser = argparse.ArgumentParser(
        description="Run selective test scenarios from testdata.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --first 5           # Run first 5 scenarios
  %(prog)s --last 3            # Run last 3 scenarios  
  %(prog)s --range 2-5         # Run scenarios 2 through 5
  %(prog)s --scenarios 1,3,7   # Run specific scenarios 1, 3, and 7
  %(prog)s                     # Run all scenarios
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--first', type=int, metavar='N',
                      help='Run first N scenarios')
    group.add_argument('--last', type=int, metavar='N', 
                      help='Run last N scenarios')
    group.add_argument('--range', type=str, metavar='START-END',
                      help='Run scenarios in range (e.g., 2-5)')
    group.add_argument('--scenarios', type=str, metavar='LIST',
                      help='Run specific scenarios (e.g., 1,3,7)')
    
    parser.add_argument('--headless', action='store_true',
                       help='Run tests in headless mode')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    return parser.parse_args()

def select_scenarios(scenarios, args):
    """Select scenarios based on command line arguments."""
    total_scenarios = len(scenarios)
    
    if total_scenarios == 0:
        print("❌ No scenarios found in testdata.csv")
        return []
    
    print(f"📊 Total scenarios available: {total_scenarios}")
    
    # If no selection arguments, run all
    if not any([args.first, args.last, args.range, args.scenarios]):
        print("🔄 Running ALL scenarios")
        return list(enumerate(scenarios, 1))
    
    selected_scenarios = []
    
    if args.first:
        n = min(args.first, total_scenarios)
        selected_scenarios = list(enumerate(scenarios[:n], 1))
        print(f"🔢 Running FIRST {n} scenarios")
        
    elif args.last:
        n = min(args.last, total_scenarios)
        start_idx = max(0, total_scenarios - n)
        selected_scenarios = list(enumerate(scenarios[start_idx:], start_idx + 1))
        print(f"🔢 Running LAST {n} scenarios")
        
    elif args.range:
        try:
            start, end = map(int, args.range.split('-'))
            start = max(1, start)
            end = min(total_scenarios, end)
            if start <= end:
                selected_scenarios = list(enumerate(scenarios[start-1:end], start))
                print(f"🔢 Running scenarios {start} to {end}")
            else:
                print(f"❌ Invalid range: {args.range}")
                return []
        except ValueError:
            print(f"❌ Invalid range format: {args.range}. Use format like '2-5'")
            return []
            
    elif args.scenarios:
        try:
            scenario_nums = [int(x.strip()) for x in args.scenarios.split(',')]
            selected_scenarios = []
            for num in scenario_nums:
                if 1 <= num <= total_scenarios:
                    selected_scenarios.append((num, scenarios[num-1]))
                else:
                    print(f"⚠️  Scenario {num} is out of range (1-{total_scenarios})")
            print(f"🔢 Running specific scenarios: {[num for num, _ in selected_scenarios]}")
        except ValueError:
            print(f"❌ Invalid scenarios format: {args.scenarios}. Use format like '1,3,7'")
            return []
    
    return selected_scenarios

def run_tests_for_scenario(scenario_data, scenario_index, scenario_name, args):
    """Run the complete test suite for a single scenario."""
    print(f"\n{'='*60}")
    print(f"RUNNING SCENARIO {scenario_index}: {scenario_name}")
    print(f"{'='*60}")
    
    # Set environment variables for this scenario
    os.environ['CURRENT_SCENARIO'] = str(scenario_index)
    os.environ['TEST_USERNAME'] = scenario_data.get('username', 'alexsingh')
    os.environ['TEST_PASSWORD'] = scenario_data.get('password', 'demo123')
    
    if args.headless:
        os.environ['HEADLESS'] = '1'
    
    # Create scenario-specific report name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"scenario_{scenario_index}_{scenario_name}_{timestamp}.html"
    
    # Build pytest command
    cmd = [
        sys.executable, '-m', 'pytest', 
        '--html', f'reports/{report_name}',
        '--self-contained-html'
    ]
    
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    try:
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print(f"✅ Scenario {scenario_index}: ALL TESTS PASSED")
        else:
            print(f"❌ Scenario {scenario_index}: SOME TESTS FAILED")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Scenario {scenario_index}: ERROR - {e}")
        return 1

def main():
    """Main execution function."""
    args = parse_arguments()
    
    print("🔍 Loading test scenarios from testdata.csv...")
    
    # Load all scenarios
    scenarios = load_test_data()
    
    if not scenarios:
        print("❌ No scenarios found in testdata.csv")
        return 1
    
    # Select scenarios based on arguments
    selected_scenarios = select_scenarios(scenarios, args)
    
    if not selected_scenarios:
        print("❌ No scenarios selected")
        return 1
    
    # Create reports directory
    os.makedirs('reports', exist_ok=True)
    
    # Track results
    total_scenarios = len(selected_scenarios)
    passed_scenarios = 0
    failed_scenarios = 0
    
    print(f"\n🚀 Starting execution of {total_scenarios} scenarios...")
    
    # Run tests for each selected scenario
    for scenario_index, scenario_data in selected_scenarios:
        scenario_name = scenario_data.get('scenario_name', f'Scenario_{scenario_index}')
        
        print(f"\n📋 Scenario {scenario_index}/{len(scenarios)}: {scenario_name}")
        if args.verbose:
            print(f"   Username: {scenario_data.get('username', 'N/A')}")
            print(f"   Estimate CPT: {scenario_data.get('estimate_cpt', 'N/A')}")
            print(f"   Claim CPT: {scenario_data.get('claim_cpt', 'N/A')}")
            print(f"   Provider Specialty: {scenario_data.get('provider_specialty', 'N/A')}")
        
        result = run_tests_for_scenario(scenario_data, scenario_index, scenario_name, args)
        
        if result == 0:
            passed_scenarios += 1
        else:
            failed_scenarios += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Selected Scenarios: {total_scenarios}")
    print(f"✅ Passed: {passed_scenarios}")
    print(f"❌ Failed: {failed_scenarios}")
    
    if failed_scenarios == 0:
        print(f"\n🎉 ALL SELECTED SCENARIOS COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print(f"\n⚠️  {failed_scenarios} scenarios had failures. Check reports for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())