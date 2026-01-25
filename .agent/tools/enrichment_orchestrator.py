#!/usr/bin/env python3
"""
Enrichment Orchestrator
=======================
SMoC Role: Orchestrator | Domain: Enrichment

Orchestrates the task enrichment pipeline:
0. REFINERY                     → Pre-atomize context for efficient AI queries
1. triage_inbox.py --score      → Score all opportunities
2. confidence_validator.py --all    → AI-assess tasks needing boost
3. batch_promote.py --threshold 85  → Auto-promote Grade A+ opps

This is the ORCHESTRATOR, not the implementation.
The implementation is in the existing tools.

Usage:
    # Run full pipeline
    python enrichment_orchestrator.py

    # Dry run
    python enrichment_orchestrator.py --dry-run

    # Skip refinery (use cached chunks)
    python enrichment_orchestrator.py --skip-refinery

    # Run as cloud function entry point
    python enrichment_orchestrator.py --cloud
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
REFINERY_PATH = REPO_ROOT / "context-management" / "tools" / "ai" / "aci" / "refinery.py"
CHUNKS_DIR = REPO_ROOT / ".agent" / "intelligence" / "chunks"


def run_tool(name: str, args: list = None, dry_run: bool = False) -> bool:
    """Run an existing tool script."""
    tool_path = SCRIPT_DIR / name
    if not tool_path.exists():
        print(f"ERROR: {tool_path} not found")
        return False

    cmd = [sys.executable, str(tool_path)] + (args or [])

    print(f"\n{'='*60}")
    print(f"RUNNING: {name} {' '.join(args or [])}")
    print(f"{'='*60}")

    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(cmd)}")
        return True

    try:
        result = subprocess.run(cmd, timeout=600)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {name}")
        return False
    except Exception as e:
        print(f"ERROR running {name}: {e}")
        return False


def run_refinery(dry_run: bool = False) -> bool:
    """
    Run REFINERY to pre-atomize context.

    Atomizes key directories into chunks for efficient AI queries:
    - .agent/ (task registry, specs)
    - context-management/tools/ai/ (ACI tools)
    - standard-model-of-code/src/core/ (pipeline core)
    """
    if not REFINERY_PATH.exists():
        print(f"WARNING: REFINERY not found at {REFINERY_PATH}")
        return False

    # Directories to atomize
    targets = [
        (REPO_ROOT / ".agent", "agent_chunks.json"),
        (REPO_ROOT / "context-management" / "tools" / "ai" / "aci", "aci_chunks.json"),
        (REPO_ROOT / "standard-model-of-code" / "src" / "core", "core_chunks.json"),
    ]

    print(f"\n{'='*60}")
    print("REFINERY - Pre-atomizing context")
    print(f"{'='*60}")

    if dry_run:
        for target_dir, output_name in targets:
            print(f"[DRY RUN] Would atomize: {target_dir.name} → {output_name}")
        return True

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    success = True

    for target_dir, output_name in targets:
        if not target_dir.exists():
            print(f"  SKIP: {target_dir} not found")
            continue

        output_path = CHUNKS_DIR / output_name
        cmd = [
            sys.executable, str(REFINERY_PATH),
            str(target_dir),
            "--export", str(output_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Parse chunk count from output
                for line in result.stdout.split('\n'):
                    if 'total chunks' in line.lower():
                        print(f"  OK: {target_dir.name} → {line.strip()}")
                        break
                else:
                    print(f"  OK: {target_dir.name} → {output_name}")
            else:
                print(f"  FAIL: {target_dir.name}")
                success = False
        except Exception as e:
            print(f"  ERROR: {target_dir.name}: {e}")
            success = False

    return success


def main():
    parser = argparse.ArgumentParser(description="Enrichment Orchestrator")
    parser.add_argument("--dry-run", "-n", action="store_true")
    parser.add_argument("--skip-refinery", action="store_true", help="Skip REFINERY step (use cached chunks)")
    parser.add_argument("--cloud", action="store_true", help="Cloud function mode")
    args = parser.parse_args()

    print("=" * 60)
    print("AUTONOMOUS ENRICHMENT PIPELINE")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Step 0: REFINERY (pre-atomize context)
    if not args.skip_refinery:
        print("\n[0/4] REFINERY - Pre-atomizing context...")
        run_refinery(args.dry_run)
    else:
        print("\n[0/4] REFINERY - Skipped (using cached chunks)")

    # Step 1: Triage (score all opportunities)
    print("\n[1/4] TRIAGE - Scoring opportunities...")
    run_tool("triage_inbox.py", ["--score"], args.dry_run)

    # Step 2: Boost (AI-assess tasks needing work)
    print("\n[2/4] BOOST - AI assessment...")
    run_tool("confidence_validator.py", ["--all"], args.dry_run)

    # Step 3: Promote (auto-promote Grade A+)
    print("\n[3/4] PROMOTE - Auto-promoting Grade A+ opportunities...")
    run_tool("batch_promote.py", ["--threshold", "85", "--auto"], args.dry_run)

    print("\n" + "=" * 60)
    print(f"ENRICHMENT COMPLETE: {datetime.now().isoformat()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
