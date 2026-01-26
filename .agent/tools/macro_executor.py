#!/usr/bin/env python3
"""
Macro Executor
==============
SMoC Role: Engine | Domain: Automation

Executes recorded action patterns (macros) from .agent/macros/library/.

Validated Architecture (2026-01-25):
- Follows task_store.py pattern for YAML handling
- Uses ruamel.yaml for safe round-trip editing
- Supports step-by-step execution with variable capture
- Logs execution history to macro files

Usage:
    ./macro_executor.py list                     # List all macros
    ./macro_executor.py show MACRO-001           # Show macro details
    ./macro_executor.py run MACRO-001            # Execute a macro
    ./macro_executor.py run MACRO-001 --dry-run  # Preview execution
    ./macro_executor.py history MACRO-001        # Show execution history

Part of S13 (Macro Registry subsystem).
See: .agent/macros/INDEX.md
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.yaml_utils import load_yaml_preserve as load_yaml, save_yaml_preserve as save_yaml

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
MACROS_DIR = REPO_ROOT / ".agent" / "macros"
LIBRARY_DIR = MACROS_DIR / "library"
LOGS_DIR = MACROS_DIR / "logs"
OUTPUT_DIR = REPO_ROOT / ".agent" / "intelligence"

# Colors for CLI output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color


def ensure_dirs():
    """Create macro directories if they don't exist."""
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_macro(macro_id: str) -> tuple[Path, dict]:
    """Load a macro by ID."""
    # Normalize ID
    if not macro_id.startswith("MACRO-"):
        macro_id = f"MACRO-{macro_id}"

    # Find macro file (could be MACRO-001.yaml or MACRO-001-name.yaml)
    for pattern in [f"{macro_id}.yaml", f"{macro_id}-*.yaml"]:
        matches = list(LIBRARY_DIR.glob(pattern))
        if matches:
            path = matches[0]
            return path, load_yaml(path)

    raise FileNotFoundError(f"Macro {macro_id} not found in {LIBRARY_DIR}")


def status_emoji(status: str) -> str:
    """Get emoji for macro status."""
    return {
        "DRAFT": "📝",
        "TESTED": "✓",
        "PRODUCTION": "🚀",
        "DEPRECATED": "⚠️",
    }.get(status.upper(), "?")


def outcome_emoji(outcome: str) -> str:
    """Get emoji for execution outcome."""
    return {
        "SUCCESS": "✓",
        "FAILURE": "✗",
        "PARTIAL": "⚠",
        "SKIPPED": "○",
    }.get(outcome.upper(), "?")


class MacroExecutor:
    """Executes macro steps with variable capture and logging."""

    def __init__(self, macro_path: Path, macro_data: dict, dry_run: bool = False):
        self.path = macro_path
        self.data = macro_data
        self.dry_run = dry_run
        self.variables: dict[str, Any] = {}
        self.step_results: list[dict] = []
        self.start_time = None

    def check_preconditions(self) -> tuple[bool, list[str]]:
        """Check all preconditions before execution."""
        failed = []
        preconditions = self.data.get("preconditions", [])

        for pre in preconditions:
            condition = pre.get("condition", "")
            required = pre.get("required", True)

            # Check environment variable conditions
            if "is set" in condition.lower():
                var_name = condition.split()[0]
                if var_name.startswith("env."):
                    var_name = var_name[4:]
                if not os.environ.get(var_name):
                    msg = f"Environment variable {var_name} not set"
                    if required:
                        failed.append(msg)
                    else:
                        print(f"{YELLOW}WARNING: {msg} (optional){NC}")

            # Check file existence conditions
            elif "exists" in condition.lower():
                parts = condition.split()
                for part in parts:
                    if part.startswith(".") or part.startswith("/"):
                        check_path = REPO_ROOT / part if not part.startswith("/") else Path(part)
                        if not check_path.exists():
                            msg = f"Path does not exist: {part}"
                            if required:
                                failed.append(msg)
                            else:
                                print(f"{YELLOW}WARNING: {msg} (optional){NC}")
                        break

        return len(failed) == 0, failed

    def interpolate(self, text: str) -> str:
        """Replace {variable} placeholders with captured values."""
        if not isinstance(text, str):
            return text

        result = text
        # Built-in variables
        now = datetime.now(timezone.utc)
        result = result.replace("{date}", now.strftime("%Y%m%d"))
        result = result.replace("{timestamp}", now.isoformat())

        # Captured variables from previous steps
        for var_name, var_value in self.variables.items():
            placeholder = "{" + var_name + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(var_value))

        return result

    def execute_step(self, step: dict) -> dict:
        """Execute a single macro step."""
        step_id = step.get("id", "unknown")
        tool = step.get("tool", "")
        params = step.get("params", {})
        output_var = step.get("output_var")
        on_failure = step.get("on_failure", "stop")
        expect = step.get("expect")

        result = {
            "step_id": step_id,
            "tool": tool,
            "outcome": "SKIPPED",
            "output": None,
            "error": None,
        }

        print(f"\n{CYAN}[{step_id}]{NC} {step.get('description', tool)}")

        if self.dry_run:
            print(f"  {YELLOW}DRY-RUN: Would execute {tool}{NC}")
            result["outcome"] = "SKIPPED"
            return result

        try:
            if tool == "Bash":
                command = self.interpolate(params.get("command", ""))
                print(f"  {BLUE}$ {command[:80]}...{NC}" if len(command) > 80 else f"  {BLUE}$ {command}{NC}")

                proc = subprocess.run(
                    command,
                    shell=True,
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                result["output"] = proc.stdout
                result["error"] = proc.stderr if proc.returncode != 0 else None
                result["exit_code"] = proc.returncode

                if proc.returncode == 0:
                    result["outcome"] = "SUCCESS"
                    print(f"  {GREEN}OK{NC}")
                else:
                    result["outcome"] = "FAILURE"
                    print(f"  {RED}FAILED (exit {proc.returncode}){NC}")
                    if proc.stderr:
                        print(f"  {RED}{proc.stderr[:200]}{NC}")

            elif tool == "Task":
                # Task tool requires AI agent - log as manual requirement
                print(f"  {YELLOW}MANUAL: This step requires AI agent execution{NC}")
                print(f"  Prompt: {params.get('prompt', '')[:100]}...")
                result["outcome"] = "SKIPPED"
                result["output"] = "Requires manual AI execution"

            elif tool == "Write":
                file_path = self.interpolate(params.get("file_path", ""))
                content = self.interpolate(params.get("content", ""))

                if file_path.startswith("."):
                    file_path = str(REPO_ROOT / file_path)

                write_path = Path(file_path)
                write_path.parent.mkdir(parents=True, exist_ok=True)
                write_path.write_text(content)

                result["outcome"] = "SUCCESS"
                result["output"] = f"Written to {file_path}"
                print(f"  {GREEN}Written: {file_path}{NC}")

            elif tool in ["Read", "Grep", "Glob"]:
                # These are read-only tools - simulate for now
                print(f"  {YELLOW}INFO: {tool} execution simulated{NC}")
                result["outcome"] = "SUCCESS"
                result["output"] = f"{tool} executed (simulated)"

            else:
                print(f"  {RED}Unknown tool: {tool}{NC}")
                result["outcome"] = "FAILURE"
                result["error"] = f"Unknown tool: {tool}"

            # Check expectation
            if expect and result["outcome"] == "SUCCESS":
                if "exit_code" in expect and result.get("exit_code") != 0:
                    result["outcome"] = "FAILURE"
                    result["error"] = f"Expected {expect}, got exit_code={result.get('exit_code')}"

            # Capture output variable
            if output_var and result["output"]:
                self.variables[output_var] = result["output"]

        except subprocess.TimeoutExpired:
            result["outcome"] = "FAILURE"
            result["error"] = "Step timed out after 5 minutes"
            print(f"  {RED}TIMEOUT{NC}")

        except Exception as e:
            result["outcome"] = "FAILURE"
            result["error"] = str(e)
            print(f"  {RED}ERROR: {e}{NC}")

        self.step_results.append(result)

        # Handle failure
        if result["outcome"] == "FAILURE":
            if on_failure == "stop":
                raise RuntimeError(f"Step {step_id} failed: {result['error']}")
            elif on_failure == "continue":
                print(f"  {YELLOW}Continuing despite failure...{NC}")

        return result

    def run(self) -> dict:
        """Execute all macro steps."""
        self.start_time = datetime.now(timezone.utc)
        macro_id = self.data.get("id", "UNKNOWN")
        macro_name = self.data.get("name", "Untitled")

        print(f"\n{'='*60}")
        print(f"EXECUTING: {macro_id} - {macro_name}")
        print(f"{'='*60}")

        if self.dry_run:
            print(f"{YELLOW}DRY-RUN MODE - No changes will be made{NC}")

        # Check preconditions
        ok, failures = self.check_preconditions()
        if not ok:
            print(f"\n{RED}PRECONDITION FAILURES:{NC}")
            for f in failures:
                print(f"  - {f}")
            return {
                "outcome": "FAILURE",
                "reason": "Preconditions not met",
                "failures": failures,
            }

        # Execute steps
        steps = self.data.get("steps", [])
        print(f"\n{len(steps)} steps to execute...")

        try:
            for step in steps:
                self.execute_step(step)
        except RuntimeError as e:
            print(f"\n{RED}EXECUTION HALTED: {e}{NC}")
            return self._finalize("FAILURE", str(e))

        # Check success criteria
        success_criteria = self.data.get("success_criteria", [])
        criteria_met = self._check_success_criteria(success_criteria)

        if criteria_met:
            return self._finalize("SUCCESS")
        else:
            return self._finalize("PARTIAL", "Not all success criteria met")

    def _check_success_criteria(self, criteria: list) -> bool:
        """Check if all success criteria are met."""
        # For now, basic check - all non-FAILURE steps
        failures = [r for r in self.step_results if r["outcome"] == "FAILURE"]
        if failures:
            return False
        return True

    def _finalize(self, outcome: str, reason: str = None) -> dict:
        """Finalize execution and log results."""
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - self.start_time).total_seconds() * 1000)

        execution_record = {
            "timestamp": self.start_time.isoformat(),
            "trigger": "manual",
            "outcome": outcome,
            "duration_ms": duration_ms,
            "dry_run": self.dry_run,
        }

        if reason:
            execution_record["reason"] = reason

        # Log to macro file (if not dry run)
        if not self.dry_run:
            if "executions" not in self.data:
                self.data["executions"] = []
            self.data["executions"].append(execution_record)
            save_yaml(self.path, self.data)

            # Also write to logs directory
            macro_id = self.data.get("id", "UNKNOWN")
            log_dir = LOGS_DIR / macro_id
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{self.start_time.strftime('%Y%m%d_%H%M%S')}.yaml"
            log_data = {
                "macro_id": macro_id,
                "execution": execution_record,
                "steps": self.step_results,
                "variables": dict(self.variables),
            }
            save_yaml(log_file, log_data)

        # Print summary
        emoji = outcome_emoji(outcome)
        color = GREEN if outcome == "SUCCESS" else (YELLOW if outcome == "PARTIAL" else RED)
        print(f"\n{'='*60}")
        print(f"{color}{emoji} OUTCOME: {outcome}{NC}")
        print(f"Duration: {duration_ms}ms")
        if reason:
            print(f"Reason: {reason}")
        print(f"{'='*60}\n")

        return execution_record


# =============================================================================
# CLI COMMANDS
# =============================================================================

def cmd_list(args):
    """List all macros."""
    ensure_dirs()

    macros = []
    for macro_file in LIBRARY_DIR.glob("MACRO-*.yaml"):
        data = load_yaml(macro_file)
        if data:
            macros.append(data)

    print(f"\n{'='*65}")
    print(f"MACRO REGISTRY ({len(macros)} macros)")
    print(f"{'='*65}\n")

    if not macros:
        print("No macros found. Create one in .agent/macros/library/")
        return

    # Group by status
    by_status = {}
    for m in macros:
        status = m.get("status", "DRAFT")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(m)

    for status in ["PRODUCTION", "TESTED", "DRAFT", "DEPRECATED"]:
        if status in by_status:
            print(f"{status}:")
            for m in by_status[status]:
                emoji = status_emoji(status)
                mid = m.get("id", "?")
                name = m.get("name", "Untitled")[:40]
                trigger = m.get("trigger", {}).get("type", "manual")
                print(f"  {emoji} {mid:12} {name:40} [{trigger}]")
            print()


def cmd_show(args):
    """Show macro details."""
    try:
        path, macro = load_macro(args.macro_id)
        print(f"\n{path.name}")
        print("-" * 60)
        if USE_RUAMEL:
            yaml.dump(macro, sys.stdout)
        else:
            print(pyyaml.dump(macro, default_flow_style=False))
    except FileNotFoundError as e:
        print(f"{RED}Error: {e}{NC}")
        sys.exit(1)


def cmd_run(args):
    """Run a macro."""
    try:
        path, macro = load_macro(args.macro_id)

        # Check status
        status = macro.get("status", "DRAFT")
        if status == "DEPRECATED":
            print(f"{RED}Cannot run deprecated macro: {args.macro_id}{NC}")
            sys.exit(1)

        if status == "DRAFT" and not args.force:
            print(f"{YELLOW}WARNING: Macro is in DRAFT status. Use --force to run anyway.{NC}")
            sys.exit(1)

        executor = MacroExecutor(path, macro, dry_run=args.dry_run)
        result = executor.run()

        sys.exit(0 if result["outcome"] == "SUCCESS" else 1)

    except FileNotFoundError as e:
        print(f"{RED}Error: {e}{NC}")
        sys.exit(1)


def cmd_history(args):
    """Show execution history for a macro."""
    try:
        path, macro = load_macro(args.macro_id)
        executions = macro.get("executions", [])

        macro_id = macro.get("id", "UNKNOWN")
        print(f"\n{'='*65}")
        print(f"EXECUTION HISTORY: {macro_id}")
        print(f"{'='*65}\n")

        if not executions:
            print("No executions recorded.")
            return

        for i, ex in enumerate(executions[-10:], 1):  # Last 10
            emoji = outcome_emoji(ex.get("outcome", "?"))
            ts = ex.get("timestamp", "?")[:19]
            outcome = ex.get("outcome", "?")
            duration = ex.get("duration_ms", "?")
            dry = " (dry-run)" if ex.get("dry_run") else ""

            print(f"{i:2}. {emoji} {ts} - {outcome}{dry} ({duration}ms)")

        # Check logs directory for more details
        log_dir = LOGS_DIR / macro_id
        if log_dir.exists():
            log_count = len(list(log_dir.glob("*.yaml")))
            if log_count > 0:
                print(f"\nDetailed logs: {log_dir} ({log_count} files)")

    except FileNotFoundError as e:
        print(f"{RED}Error: {e}{NC}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Macro Executor - Run recorded action patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    ./macro_executor.py list
    ./macro_executor.py show MACRO-001
    ./macro_executor.py run MACRO-001 --dry-run
    ./macro_executor.py run MACRO-001 --force
    ./macro_executor.py history MACRO-001
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List
    subparsers.add_parser("list", help="List all macros")

    # Show
    show_p = subparsers.add_parser("show", help="Show macro details")
    show_p.add_argument("macro_id", help="Macro ID (e.g., MACRO-001 or 001)")

    # Run
    run_p = subparsers.add_parser("run", help="Execute a macro")
    run_p.add_argument("macro_id", help="Macro ID to execute")
    run_p.add_argument("--dry-run", action="store_true", help="Preview without executing")
    run_p.add_argument("--force", action="store_true", help="Run even if DRAFT status")

    # History
    hist_p = subparsers.add_parser("history", help="Show execution history")
    hist_p.add_argument("macro_id", help="Macro ID")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "history":
        cmd_history(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
