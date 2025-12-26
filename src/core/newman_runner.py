#!/usr/bin/env python3
"""
🏃 NEWMAN RUNNER
Executes the health suite and reports system status.
"""
import sys
import os
from datetime import datetime

# Ensure we can import from local dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.newman_suite import NewmanSuite, ProbeResult

def run_health_check(exit_on_fail=False):
    """Run all health checks and print report."""
    print("🔬 NEWMAN PIPELINE VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 60)
    
    suite = NewmanSuite()
    results = suite.run_all()
    
    all_passed = True
    
    for r in results:
        status_icon = "✅"
        if r.status == "FAIL":
            status_icon = "❌"
            all_passed = False
        elif r.status == "WARN":
            status_icon = "⚠️ "
        elif r.status == "SKIP":
            status_icon = "⏭️ "
            
        print(f"{status_icon} [{r.component}]".ljust(40) + f"{r.status} ({r.latency_ms:.1f}ms)")
        print(f"    └─ {r.details}")
        if r.error:
            print(f"    ❌ Error: {r.error}")
        print()
        
    print("=" * 60)
    if all_passed:
        print(f"✨ SYSTEM HEALTHY - {len(results)} Checks Passed")
        return 0
    else:
        print("🚨 SYSTEM ISSUES DETECTED")
        if exit_on_fail:
            return 1
        return 0

if __name__ == "__main__":
    sys.exit(run_health_check(exit_on_fail=True))
