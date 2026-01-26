#!/usr/bin/env python3
"""
Trigger Engine
==============
SMoC Role: Dispatcher | Domain: Automation

Watches for trigger conditions and dispatches macros for execution.

Trigger Types:
- post_commit: Pattern match on commit message (feat(*), fix(*), etc.)
- schedule: Cron-based (handled by external scheduler, not this script)
- event: Registry events (task_promoted, opp_created)
- file_change: File modification patterns (future)
- manual: Always skipped by trigger engine

Usage:
    ./trigger_engine.py post-commit              # Check recent commit, run matching macros
    ./trigger_engine.py post-commit --dry-run    # Preview without executing
    ./trigger_engine.py check-all                # List what would trigger
    ./trigger_engine.py status                   # Show trigger engine status

Part of S13 (Macro Registry subsystem).
See: .agent/macros/INDEX.md
"""

import argparse
import fnmatch
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Use ruamel.yaml if available
try:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    USE_RUAMEL = True
except ImportError:
    import yaml as pyyaml
    yaml = None
    USE_RUAMEL = False

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
MACROS_DIR = REPO_ROOT / ".agent" / "macros"
LIBRARY_DIR = MACROS_DIR / "library"
STATE_FILE = MACROS_DIR / "trigger_state.yaml"

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    with open(path) as f:
        if USE_RUAMEL:
            return yaml.load(f)
        else:
            return pyyaml.safe_load(f)


def save_yaml(path: Path, data: dict):
    """Save YAML file."""
    with open(path, 'w') as f:
        if USE_RUAMEL:
            yaml.dump(data, f)
        else:
            pyyaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def load_state() -> dict:
    """Load trigger engine state."""
    if STATE_FILE.exists():
        return load_yaml(STATE_FILE)
    return {
        "last_check": None,
        "last_commit": None,
        "queued_macros": [],
        "execution_count": 0,
    }


def save_state(state: dict):
    """Save trigger engine state."""
    save_yaml(STATE_FILE, state)


def get_last_commit() -> dict:
    """Get information about the most recent commit."""
    try:
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        commit_hash = hash_result.stdout.strip()

        # Get commit message
        msg_result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        message = msg_result.stdout.strip()

        # Get changed files
        files_result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        files = files_result.stdout.strip().split("\n") if files_result.stdout.strip() else []

        return {
            "hash": commit_hash,
            "message": message,
            "files": files,
        }
    except Exception as e:
        print(f"{RED}Error getting commit info: {e}{NC}")
        return None


def load_all_macros() -> list[dict]:
    """Load all macros from library."""
    macros = []
    for macro_file in LIBRARY_DIR.glob("MACRO-*.yaml"):
        data = load_yaml(macro_file)
        if data:
            data["_path"] = str(macro_file)
            macros.append(data)
    return macros


def matches_commit_pattern(message: str, pattern: str) -> bool:
    """Check if commit message matches pattern."""
    # Convert macro pattern to regex
    # Examples: "feat(*)" -> "feat\(.*\)", "fix(*): *" -> "fix\(.*\): .*"
    regex_pattern = pattern
    regex_pattern = regex_pattern.replace("(", r"\(")
    regex_pattern = regex_pattern.replace(")", r"\)")
    regex_pattern = regex_pattern.replace("*", ".*")

    try:
        return bool(re.match(regex_pattern, message, re.IGNORECASE))
    except re.error:
        # Fallback to simple glob matching
        return fnmatch.fnmatch(message.lower(), pattern.lower().replace("(*)", "*"))


def find_triggered_macros(commit: dict) -> list[dict]:
    """Find macros that should be triggered by this commit."""
    triggered = []
    macros = load_all_macros()

    for macro in macros:
        # Skip non-production macros unless TESTED
        status = macro.get("status", "DRAFT")
        if status not in ["PRODUCTION", "TESTED"]:
            continue

        trigger = macro.get("trigger", {})
        trigger_type = trigger.get("type", "manual")

        # Skip manual triggers
        if trigger_type == "manual":
            continue

        # Check post_commit triggers
        if trigger_type == "post_commit":
            pattern = trigger.get("commit_pattern", "")
            if pattern and matches_commit_pattern(commit["message"], pattern):
                triggered.append(macro)

        # Check file_change triggers (future enhancement)
        # if trigger_type == "file_change":
        #     file_pattern = trigger.get("file_pattern", "")
        #     for f in commit["files"]:
        #         if fnmatch.fnmatch(f, file_pattern):
        #             triggered.append(macro)
        #             break

    return triggered


def execute_macro(macro: dict, dry_run: bool = False) -> bool:
    """Execute a macro using macro_executor.py."""
    macro_id = macro.get("id", "UNKNOWN")
    executor_path = REPO_ROOT / ".agent" / "tools" / "macro_executor.py"

    if not executor_path.exists():
        print(f"{RED}Macro executor not found: {executor_path}{NC}")
        return False

    cmd = ["python", str(executor_path), "run", macro_id]
    if dry_run:
        cmd.append("--dry-run")

    # Allow TESTED macros (they'll need --force)
    if macro.get("status") == "TESTED":
        cmd.append("--force")

    print(f"\n{BLUE}Executing: {' '.join(cmd)}{NC}")

    try:
        result = subprocess.run(cmd, cwd=REPO_ROOT)
        return result.returncode == 0
    except Exception as e:
        print(f"{RED}Execution failed: {e}{NC}")
        return False


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_post_commit(args):
    """Check recent commit and run matching macros."""
    commit = get_last_commit()
    if not commit:
        print(f"{RED}Could not get commit information{NC}")
        sys.exit(1)

    state = load_state()

    # Check if we already processed this commit
    if state.get("last_commit") == commit["hash"] and not args.force:
        print(f"{YELLOW}Commit {commit['hash'][:8]} already processed. Use --force to re-run.{NC}")
        return

    print(f"\n{YELLOW}Checking commit: {commit['hash'][:8]}{NC}")
    print(f"Message: {commit['message'][:60]}...")

    # Find triggered macros
    triggered = find_triggered_macros(commit)

    if not triggered:
        print(f"{GREEN}No macros triggered.{NC}")
        state["last_commit"] = commit["hash"]
        state["last_check"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    print(f"\n{GREEN}Found {len(triggered)} macro(s) to trigger:{NC}")
    for macro in triggered:
        print(f"  - {macro.get('id')}: {macro.get('name')}")

    # Execute triggered macros
    success_count = 0
    for macro in triggered:
        if execute_macro(macro, dry_run=args.dry_run):
            success_count += 1

    # Update state
    if not args.dry_run:
        state["last_commit"] = commit["hash"]
        state["last_check"] = datetime.now(timezone.utc).isoformat()
        state["execution_count"] = state.get("execution_count", 0) + success_count
        save_state(state)

    print(f"\n{GREEN}Executed {success_count}/{len(triggered)} macros.{NC}")


def cmd_check_all(args):
    """List all macros and their triggers."""
    macros = load_all_macros()

    print(f"\n{'='*70}")
    print("TRIGGER CONFIGURATION")
    print(f"{'='*70}\n")

    by_type = {}
    for macro in macros:
        status = macro.get("status", "DRAFT")
        if status == "DEPRECATED":
            continue

        trigger = macro.get("trigger", {})
        trigger_type = trigger.get("type", "manual")

        if trigger_type not in by_type:
            by_type[trigger_type] = []
        by_type[trigger_type].append(macro)

    for trigger_type in ["post_commit", "schedule", "event", "file_change", "manual"]:
        if trigger_type in by_type:
            print(f"{trigger_type.upper()}:")
            for m in by_type[trigger_type]:
                mid = m.get("id", "?")
                name = m.get("name", "?")[:35]
                status = m.get("status", "?")
                trigger = m.get("trigger", {})

                details = ""
                if trigger_type == "post_commit":
                    details = trigger.get("commit_pattern", "")
                elif trigger_type == "schedule":
                    details = trigger.get("schedule", "")
                elif trigger_type == "file_change":
                    details = trigger.get("file_pattern", "")

                status_color = GREEN if status == "PRODUCTION" else (YELLOW if status == "TESTED" else NC)
                print(f"  {mid:12} {name:35} {status_color}[{status}]{NC} {details}")
            print()


def cmd_status(args):
    """Show trigger engine status."""
    state = load_state()

    print(f"\n{'='*50}")
    print("TRIGGER ENGINE STATUS")
    print(f"{'='*50}\n")

    last_check = state.get("last_check", "Never")
    last_commit = state.get("last_commit", "None")[:8] if state.get("last_commit") else "None"
    exec_count = state.get("execution_count", 0)

    print(f"Last check:       {last_check}")
    print(f"Last commit:      {last_commit}")
    print(f"Total executions: {exec_count}")

    # Count macros by trigger type
    macros = load_all_macros()
    by_trigger = {}
    for m in macros:
        if m.get("status") == "DEPRECATED":
            continue
        t = m.get("trigger", {}).get("type", "manual")
        by_trigger[t] = by_trigger.get(t, 0) + 1

    print(f"\nMacros by trigger type:")
    for t, count in sorted(by_trigger.items()):
        print(f"  {t:15} {count}")

    print(f"\nState file: {STATE_FILE}")


def main():
    parser = argparse.ArgumentParser(
        description="Trigger Engine - Dispatch macros based on events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    ./trigger_engine.py post-commit              # Check and run triggered macros
    ./trigger_engine.py post-commit --dry-run    # Preview only
    ./trigger_engine.py check-all                # Show trigger configuration
    ./trigger_engine.py status                   # Engine status
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # post-commit
    pc_p = subparsers.add_parser("post-commit", help="Process post-commit triggers")
    pc_p.add_argument("--dry-run", action="store_true", help="Preview without executing")
    pc_p.add_argument("--force", action="store_true", help="Re-process even if already done")

    # check-all
    subparsers.add_parser("check-all", help="Show all trigger configurations")

    # status
    subparsers.add_parser("status", help="Show trigger engine status")

    args = parser.parse_args()

    if args.command == "post-commit":
        cmd_post_commit(args)
    elif args.command == "check-all":
        cmd_check_all(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
