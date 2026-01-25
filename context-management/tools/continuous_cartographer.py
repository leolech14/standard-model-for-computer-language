#!/usr/bin/env python3
"""
Continuous Cartographer - Repository Context System
====================================================
The primary payload for the HSL Daemon watcher.

This script maintains "Repository Context" - an always-fresh internal map
of the codebase that's never more than 15 seconds behind reality.

Architecture (3 Options):
  A) Cartographer (Primary)  - Runs Collider, updates unified_analysis.json
  B) Guardian (Secondary)    - Runs semantic verification (API cost)
  C) Researcher (Tertiary)   - Runs Perplexity research (API cost, manual only)

Usage:
    # Run full cartography (Option A only)
    python continuous_cartographer.py

    # Run with semantic verification (Option A + B)
    python continuous_cartographer.py --verify

    # Run with specific changed files (for incremental)
    python continuous_cartographer.py --files "src/foo.py,src/bar.py"

    # Check what would run (dry run)
    python continuous_cartographer.py --dry-run

    # Force verification even without code changes
    python continuous_cartographer.py --verify --force
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
VENV_PYTHON = PROJECT_ROOT / ".tools_venv/bin/python"
COLLIDER_OUTPUT = PROJECT_ROOT / "standard-model-of-code/.collider"
ANALYZE_SCRIPT = PROJECT_ROOT / "context-management/tools/ai/analyze.py"
REPORTS_DIR = PROJECT_ROOT / "context-management/reports"

# File patterns that trigger Option B (Guardian - semantic verification)
CODE_EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs', '.java', '.kt'}
CONFIG_FILES = {'semantic_models.yaml', 'analysis_sets.yaml', 'pyproject.toml'}

# ============================================================================
# HELPERS
# ============================================================================

def log(msg: str, level: str = "INFO"):
    """Log with timestamp and level."""
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌", "RUN": "🔬"}
    icon = icons.get(level, "")
    print(f"[{ts}] {icon} {msg}")


def get_python() -> str:
    """Get the correct Python interpreter."""
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


def should_verify(changed_files: List[str]) -> bool:
    """Determine if Option B (verification) should run based on changed files."""
    for f in changed_files:
        path = Path(f)
        # Check extension
        if path.suffix.lower() in CODE_EXTENSIONS:
            return True
        # Check config files
        if path.name in CONFIG_FILES:
            return True
        # Check important directories
        if 'src/' in f or 'core/' in f or 'lib/' in f or 'packages/' in f:
            return True
    return False


# ============================================================================
# OPTION A: CARTOGRAPHER (Primary - Always Runs)
# ============================================================================

def run_cartographer(target_path: Optional[Path] = None) -> bool:
    """
    Run the Collider analysis pipeline.
    Updates: .collider/unified_analysis.json (the knowledge graph)
    Cost: FREE (local CPU only)
    """
    log("Starting Cartographer (Option A: Internal Map)", "RUN")

    target = target_path or PROJECT_ROOT
    python = get_python()

    # Set up environment with correct PYTHONPATH
    env = os.environ.copy()
    smc_path = str(PROJECT_ROOT / "standard-model-of-code")
    env["PYTHONPATH"] = smc_path + os.pathsep + env.get("PYTHONPATH", "")

    try:
        # Run: collider full <target> --output .collider
        result = subprocess.run(
            [python, "-m", "cli", "full", str(target), "--output", str(COLLIDER_OUTPUT)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=smc_path,
            env=env
        )

        if result.returncode == 0:
            # Check output exists
            unified = COLLIDER_OUTPUT / "unified_analysis.json"
            if unified.exists():
                size_kb = unified.stat().st_size / 1024
                log(f"Cartographer complete: unified_analysis.json ({size_kb:.1f}KB)", "OK")
                return True
            else:
                log("Cartographer ran but no unified_analysis.json produced", "WARN")
                return False
        else:
            log(f"Cartographer failed (exit {result.returncode})", "ERROR")
            if result.stderr:
                # Only show last 3 lines of error
                lines = result.stderr.strip().split('\n')
                for line in lines[-3:]:
                    log(f"  {line}", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log("Cartographer timed out after 5 minutes", "ERROR")
        return False
    except Exception as e:
        log(f"Cartographer exception: {e}", "ERROR")
        return False


# ============================================================================
# OPTION B: GUARDIAN (Secondary - Conditional)
# ============================================================================

def run_guardian() -> bool:
    """
    Run semantic verification against Antimatter Laws.
    Updates: context-management/reports/socratic_audit_latest.md
    Cost: 1 Gemini API call
    """
    log("Starting Guardian (Option B: Semantic Verification)", "RUN")

    python = get_python()

    try:
        result = subprocess.run(
            [python, str(ANALYZE_SCRIPT), "--verify", "pipeline"],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for API call
            cwd=str(PROJECT_ROOT)
        )

        if result.returncode == 0:
            log("Guardian verification passed", "OK")
            return True
        else:
            log(f"Guardian found issues (exit {result.returncode})", "WARN")
            # Count violations in output
            violations = result.stdout.count("VIOLATION") + result.stdout.count("violation")
            if violations > 0:
                log(f"  {violations} potential violations detected", "WARN")
            return False

    except subprocess.TimeoutExpired:
        log("Guardian timed out after 2 minutes", "ERROR")
        return False
    except Exception as e:
        log(f"Guardian exception: {e}", "ERROR")
        return False


# ============================================================================
# MAIN PAYLOAD
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Continuous Cartographer - Repository Context System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--verify", action="store_true",
                        help="Also run Option B (semantic verification)")
    parser.add_argument("--files", type=str, default="",
                        help="Comma-separated list of changed files")
    parser.add_argument("--force", action="store_true",
                        help="Force verification even without code changes")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would run without executing")
    parser.add_argument("--once", action="store_true",
                        help="Alias for default behavior (compatibility)")

    args = parser.parse_args()

    # Parse changed files
    changed_files = [f.strip() for f in args.files.split(",") if f.strip()]

    # Determine what to run
    run_a = True  # Always run cartographer
    run_b = args.verify or args.force or (changed_files and should_verify(changed_files))

    if args.dry_run:
        log("=== DRY RUN ===", "INFO")
        log(f"Would run Option A (Cartographer): YES", "INFO")
        log(f"Would run Option B (Guardian): {'YES' if run_b else 'NO'}", "INFO")
        if changed_files:
            log(f"Changed files: {changed_files}", "INFO")
            log(f"Code change detected: {should_verify(changed_files)}", "INFO")
        return 0

    log("=" * 50, "INFO")
    log("CONTINUOUS CARTOGRAPHER - Repository Context", "INFO")
    log("=" * 50, "INFO")

    success = True

    # Option A: Cartographer (always)
    if run_a:
        if not run_cartographer():
            success = False

    # Option B: Guardian (conditional)
    if run_b:
        if not run_guardian():
            # Guardian failure is a warning, not a hard failure
            log("Guardian reported issues - check reports/", "WARN")

    # Summary
    log("-" * 50, "INFO")
    if success:
        log("Repository context updated successfully", "OK")
    else:
        log("Repository context update had issues", "WARN")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
