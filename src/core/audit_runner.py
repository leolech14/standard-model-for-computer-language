#!/usr/bin/env python3
"""
🔍 AUDIT RUNNER
Performs a combined health check and minimal analysis to prove the pipeline works end-to-end.
"""
from pathlib import Path
from datetime import datetime
import sys

# Ensure root is importable when invoked from CLI
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.newman_suite import NewmanSuite
try:
    from tools.prove import run_proof
except ImportError:
    # Fallback if tools package not yet installed
    import sys
    sys.path.append(str(ROOT_DIR / "tools"))
    from prove import run_proof


def _print_health(results):
    """Pretty-print health results and return boolean success."""
    print("\n🔬 NEWMAN PIPELINE VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 60)

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

    if all_passed:
        print("✨ HEALTH SUITE PASSED")
    else:
        print("🚨 HEALTH SUITE DETECTED ISSUES")
    return all_passed


def run_full_audit(target_path: str = ".", output_dir: str = "output/audit") -> int:
    """Run health checks and a quick analysis to validate the toolchain."""
    repo_path = Path(target_path).resolve()
    print("\n🧾 SPECTROMETER FULL AUDIT")
    print("=" * 60)
    print(f"Target: {repo_path}")
    print(f"Output: {output_dir}")

    if not repo_path.exists():
        print(f"❌ Target path not found: {repo_path}")
        return 1

    health_results = NewmanSuite().run_all()
    health_ok = _print_health(health_results)

    print("\n🧠 RUNNING ANALYSIS")

    analysis_ok = True
    try:
        run_proof(str(repo_path), output_dir=output_dir)
    except SystemExit as e:
        analysis_ok = (e.code == 0)
    except Exception as exc:  # noqa: BLE001
        analysis_ok = False
        print(f"❌ Analysis failed: {exc}")

    print("\n" + "=" * 60)
    if health_ok and analysis_ok:
        print("✅ AUDIT COMPLETE: pipeline is operational")
        return 0

    if not health_ok:
        print("❌ Audit failed: health suite reported issues")
    if not analysis_ok:
        print("❌ Audit failed: analysis run did not complete cleanly")
    return 1


if __name__ == "__main__":
    sys.exit(run_full_audit())
