#!/usr/bin/env python3
"""
UI Validation Tool - Headless Circuit Breaker Runner

Runs the circuit-breaker.js tests in a headless browser and reports results.
Integrates with Collider pipeline via --validate-ui flag.

Usage:
    python tools/validate_ui.py path/to/output.html
    python tools/validate_ui.py path/to/output.html --verbose
    python tools/validate_ui.py path/to/output.html --screenshot failures.png
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def validate_ui(
    html_path: str,
    verbose: bool = False,
    screenshot_path: Optional[str] = None,
    timeout_ms: int = 30000
) -> Dict[str, Any]:
    """
    Run circuit breaker tests on an HTML file using headless browser.

    Args:
        html_path: Path to the Collider HTML output
        verbose: Print detailed test results
        screenshot_path: Optional path to save screenshot on failure
        timeout_ms: Timeout for page load and tests

    Returns:
        Dict with 'passed', 'failed', 'total', 'results', 'errors'
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {
            'passed': 0,
            'failed': 0,
            'total': 0,
            'results': {},
            'errors': ['Playwright not installed. Run: pip install playwright && playwright install chromium']
        }

    html_file = Path(html_path).resolve()
    if not html_file.exists():
        return {
            'passed': 0,
            'failed': 0,
            'total': 0,
            'results': {},
            'errors': [f'HTML file not found: {html_file}']
        }

    result = {
        'passed': 0,
        'failed': 0,
        'total': 0,
        'results': {},
        'errors': [],
        'console_logs': []
    }

    with sync_playwright() as p:  # type: ignore[possibly-undefined]
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        # Capture console logs
        def handle_console(msg):
            result['console_logs'].append({
                'type': msg.type,
                'text': msg.text
            })
            if verbose and '[CIRCUIT]' in msg.text:
                print(f"  {msg.text}")

        page.on('console', handle_console)

        # Capture errors
        def handle_error(error):
            result['errors'].append(str(error))

        page.on('pageerror', handle_error)

        try:
            # Load the HTML file
            file_url = f'file://{html_file}'
            if verbose:
                print(f"Loading: {file_url}")

            page.goto(file_url, timeout=timeout_ms, wait_until='networkidle')

            # Wait for the visualization to initialize
            # Check if Graph object exists (indicates 3D-force-graph loaded)
            page.wait_for_function('typeof Graph !== "undefined"', timeout=timeout_ms)

            # Check if CIRCUIT module is available
            circuit_available = page.evaluate('typeof CIRCUIT !== "undefined"')
            if not circuit_available:
                result['errors'].append('CIRCUIT module not found - circuit-breaker.js not loaded')
                browser.close()
                return result

            # Run the circuit breaker tests
            if verbose:
                print("Running CIRCUIT.runAll()...")

            test_results = page.evaluate('''
                async () => {
                    const results = await CIRCUIT.runAll();
                    return results;
                }
            ''')

            if test_results:
                result['passed'] = test_results.get('passed', 0)
                result['failed'] = test_results.get('failed', 0)
                result['total'] = test_results.get('total', 0)
                result['results'] = test_results.get('results', {})

            # Take screenshot if failures and path provided
            if screenshot_path and result['failed'] > 0:
                page.screenshot(path=screenshot_path, full_page=True)
                if verbose:
                    print(f"Screenshot saved: {screenshot_path}")

        except PlaywrightTimeout as e:  # type: ignore[possibly-undefined]
            result['errors'].append(f'Timeout: {e}')
        except Exception as e:
            result['errors'].append(f'Error: {e}')
        finally:
            browser.close()

    return result


def print_report(result: Dict[str, Any], verbose: bool = False) -> None:
    """Print a formatted report of the validation results."""
    print("\n" + "=" * 70)
    print("CIRCUIT BREAKER VALIDATION REPORT")
    print("=" * 70)

    if result['errors']:
        print("\nJS ERRORS:")
        for error in result['errors']:
            print(f"  - {error}")

    total = result['total']
    passed = result['passed']
    failed = result['failed']

    if total == 0:
        print("\nNo tests were run.")
        return

    pct = (passed / total) * 100

    print(f"\nResults: {passed}/{total} passed ({pct:.1f}%)")

    if verbose and result['results']:
        print("\n" + "-" * 70)
        print("DETAILED RESULTS")
        print("-" * 70)

        for name, test_result in result['results'].items():
            symbol = "+" if test_result.get('passed') else "X"

            if test_result.get('passed'):
                print(f"\n[{symbol}] {name} - PASS")
            else:
                print(f"\n[{symbol}] {name} - FAIL")

                # Error message
                error = test_result.get('error')
                if error:
                    print(f"    Error: {error}")

                # Expected vs Actual
                expected = test_result.get('expected')
                actual = test_result.get('actual')
                if expected is not None or actual is not None:
                    print(f"    Expected: {expected}")
                    print(f"    Actual:   {actual}")

                # State exists check
                state_exists = test_result.get('stateExists')
                if state_exists is False:
                    print(f"    State: NOT DEFINED (binding chain broken)")

                # Trace chain
                trace = test_result.get('trace')
                if trace and isinstance(trace, dict) and trace.get('chain'):
                    print(f"    Trace:")
                    for step in trace['chain']:
                        print(f"      {step}")

                # Fix recommendation
                fix = test_result.get('fix')
                if fix:
                    print(f"    FIX: {fix}")

    # Summary
    print("\n" + "=" * 70)
    if failed == 0:
        print("STATUS: ALL TESTS PASSED")
    else:
        print(f"STATUS: {failed} TESTS FAILED")

        # Categorize failures by root cause
        missing_elements = []
        state_undefined = []
        graph_issues = []
        validation_failed = []

        for name, r in result['results'].items():
            if r.get('passed'):
                continue
            if not r.get('elementFound'):
                missing_elements.append((name, r))
            elif r.get('stateExists') is False:
                state_undefined.append((name, r))
            elif r.get('error') and 'Graph' in str(r.get('error', '')):
                graph_issues.append((name, r))
            else:
                validation_failed.append((name, r))

        # Print by category
        if missing_elements:
            print("\n[MISSING DOM ELEMENTS]")
            for name, r in missing_elements:
                print(f"  {name}: Add #{r.get('trace', {}).get('element', {}).get('id', name)} to template.html")

        if state_undefined:
            print("\n[STATE NOT INITIALIZED]")
            states_needed = set()
            for name, r in state_undefined:
                trace = r.get('trace', {})
                state_path = trace.get('state', {}).get('path', '')
                if state_path:
                    states_needed.add(state_path.split('.')[0])
            if states_needed:
                print(f"  Root cause: {', '.join(states_needed)} not defined")
                print(f"  Fix: Ensure these objects are created in app.js before UI bindings")
            for name, r in state_undefined:
                trace = r.get('trace', {})
                state_path = trace.get('state', {}).get('path', '')
                print(f"    - {name}: needs {state_path}")

        if graph_issues:
            print("\n[GRAPH NOT READY]")
            print(f"  Root cause: Graph object not initialized when tests run")
            print(f"  Fix: Ensure Graph is created before CIRCUIT.runAll() or defer tests")
            for name, r in graph_issues:
                print(f"    - {name}: {r.get('error', 'Unknown error')}")

        if validation_failed:
            print("\n[VALIDATION LOGIC FAILED]")
            for name, r in validation_failed:
                expected = r.get('expected')
                actual = r.get('actual')
                fix = r.get('fix', '')
                print(f"  {name}: expected {expected}, got {actual}")
                if fix:
                    print(f"    -> {fix}")

        # Quick fix summary
        print("\n" + "-" * 70)
        print("QUICK FIX CHECKLIST:")
        print("-" * 70)
        if state_undefined:
            print("[ ] Initialize APPEARANCE_STATE in app.js before binding sliders")
        if graph_issues:
            print("[ ] Ensure Graph is created before physics controls are bound")
        if missing_elements:
            print("[ ] Add missing elements to template.html")
        if validation_failed:
            print("[ ] Check event handler bindings for validation failures")


def main():
    parser = argparse.ArgumentParser(
        description='Validate Collider HTML output using headless circuit breaker tests'
    )
    parser.add_argument('html_path', help='Path to the Collider HTML output file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed results')
    parser.add_argument('--screenshot', help='Save screenshot on failure to this path')
    parser.add_argument('--timeout', type=int, default=30000, help='Timeout in milliseconds (default: 30000)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    if not PLAYWRIGHT_AVAILABLE:
        print("ERROR: Playwright not installed.")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)

    result = validate_ui(
        args.html_path,
        verbose=args.verbose,
        screenshot_path=args.screenshot,
        timeout_ms=args.timeout
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result, verbose=args.verbose)

    # Exit with error code if tests failed
    if result['failed'] > 0 or result['errors']:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
