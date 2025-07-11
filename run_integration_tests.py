#!/usr/bin/env python3
"""
Integration Test Runner for Backtrader Alerts System
Runs all integration tests with comprehensive reporting
"""
import unittest
import sys
import os
import time
from datetime import datetime

def print_header():
    """Print test suite header"""
    print("=" * 80)
    print("🧪 BACKTRADER ALERTS - INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_section(title):
    """Print section header"""
    print(f"\n{'🔧' if 'Test' in title else '📊'} {title}")
    print("-" * 60)

def run_test_module(module_name, description):
    """Run a specific test module"""
    print_section(f"Running {description}")
    
    try:
        # Import and run the test module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_name)
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Calculate results
        tests_run = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
        success_rate = ((tests_run - failures - errors) / tests_run * 100) if tests_run > 0 else 0
        duration = end_time - start_time
        
        # Print summary
        print(f"\n📊 {description} Results:")
        print(f"   Tests run: {tests_run}")
        print(f"   Successes: {tests_run - failures - errors}")
        print(f"   Failures: {failures}")
        print(f"   Errors: {errors}")
        print(f"   Skipped: {skipped}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Duration: {duration:.2f}s")
        
        return {
            'module': module_name,
            'description': description,
            'tests_run': tests_run,
            'successes': tests_run - failures - errors,
            'failures': failures,
            'errors': errors,
            'skipped': skipped,
            'success_rate': success_rate,
            'duration': duration
        }
        
    except Exception as e:
        print(f"❌ Failed to run {description}: {e}")
        return {
            'module': module_name,
            'description': description,
            'tests_run': 0,
            'successes': 0,
            'failures': 1,
            'errors': 0,
            'skipped': 0,
            'success_rate': 0.0,
            'duration': 0.0
        }

def print_overall_summary(results):
    """Print overall test summary"""
    print("\n" + "=" * 80)
    print("📈 OVERALL INTEGRATION TEST SUMMARY")
    print("=" * 80)
    
    total_tests = sum(r['tests_run'] for r in results)
    total_successes = sum(r['successes'] for r in results)
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    total_duration = sum(r['duration'] for r in results)
    overall_success_rate = (total_successes / total_tests * 100) if total_tests > 0 else 0
    
    print(f"🏆 TOTAL RESULTS:")
    print(f"   Test modules: {len(results)}")
    print(f"   Total tests: {total_tests}")
    print(f"   Successes: {total_successes}")
    print(f"   Failures: {total_failures}")
    print(f"   Errors: {total_errors}")
    print(f"   Skipped: {total_skipped}")
    print(f"   Overall success rate: {overall_success_rate:.1f}%")
    print(f"   Total duration: {total_duration:.2f}s")
    
    print(f"\n📋 MODULE BREAKDOWN:")
    for result in results:
        status = "✅" if result['success_rate'] == 100.0 else "⚠️" if result['success_rate'] >= 80.0 else "❌"
        print(f"   {status} {result['description']}: {result['success_rate']:.1f}% ({result['successes']}/{result['tests_run']})")
    
    # Overall status
    if overall_success_rate == 100.0:
        print(f"\n🎉 ALL INTEGRATION TESTS PASSED! System ready for production.")
    elif overall_success_rate >= 90.0:
        print(f"\n✅ Integration tests mostly passed. Minor issues to review.")
    elif overall_success_rate >= 70.0:
        print(f"\n⚠️ Integration tests partially passed. Some issues need attention.")
    else:
        print(f"\n❌ Integration tests failed. Major issues require fixing.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def main():
    """Main test runner"""
    # Print header
    print_header()
    
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Define test modules to run
    test_modules = [
        ('tests.integration.test_data_flow', 'Data Flow Integration Tests'),
        ('tests.integration.test_strategy_execution', 'Strategy Execution Integration Tests'),
        ('tests.integration.test_multi_timeframe', 'Multi-Timeframe Workflow Tests'),
        ('tests.integration.test_end_to_end', 'End-to-End Integration Tests')
    ]
    
    # Run all test modules
    results = []
    overall_start_time = time.time()
    
    for module_name, description in test_modules:
        result = run_test_module(module_name, description)
        results.append(result)
    
    overall_end_time = time.time()
    
    # Print summary
    print_overall_summary(results)
    
    # Return exit code based on results
    all_passed = all(r['failures'] == 0 and r['errors'] == 0 for r in results)
    return 0 if all_passed else 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner failed: {e}")
        sys.exit(1)