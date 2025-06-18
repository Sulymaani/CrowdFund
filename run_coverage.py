"""
Test coverage runner script for CrowdFund application.
Run this script to generate test coverage reports.
"""
import os
import sys
import coverage
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()
    
    # Setup Django environment
    os.environ['DJANGO_SETTINGS_MODULE'] = 'crowdfund.settings'
    django.setup()
    
    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # If specific apps or test modules are provided as arguments, test only those
    test_labels = sys.argv[1:] if len(sys.argv) > 1 else ["accounts", "campaigns", "donations", "organizations"]
    
    failures = test_runner.run_tests(test_labels)
    
    # Stop coverage measurement and save results
    cov.stop()
    cov.save()
    
    # Generate coverage reports
    print("\nCoverage Summary:")
    cov.report()
    
    # Generate HTML report
    print("\nGenerating HTML report...")
    cov.html_report()
    
    print("\nHTML report generated in coverage_html_report/index.html")
    
    # Exit with appropriate code
    sys.exit(bool(failures))
