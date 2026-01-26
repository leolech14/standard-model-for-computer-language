#!/usr/bin/env python3
"""
Add Task Steps - Add individual steps to a task.

Steps are the atomic actions within a task (STEP-01, STEP-02, etc.)
following the hierarchy: ROADMAP > SPRINT > TASK > STEP

Usage:
    ./add_task_steps.py TASK-005 "Read the existing implementation"
    ./add_task_steps.py TASK-005 "Implement the new feature" --depends-on STEP-01
    ./add_task_steps.py TASK-005 --list   # List all steps
    ./add_task_steps.py TASK-005 --complete STEP-01  # Mark step complete

Step Status: PENDING -> IN_PROGRESS -> DONE | SKIPPED
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from utils.yaml_utils import load_yaml_preserve as load_yaml, save_yaml_preserve as save_yaml

SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
ACTIVE_DIR = AGENT_DIR / "registry" / "active"

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def get_next_step_id(steps: list) -> str:
    """Get next step ID (STEP-01, STEP-02, etc.)."""
    max_num = 0
    for step in steps:
        step_id = step.get("id", "")
        if step_id.startswith("STEP-"):
            try:
                num = int(step_id.split("-")[1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass
    return f"STEP-{max_num + 1:02d}"


def add_step(task_path: Path, action: str, depends_on: list = None) -> dict:
    """Add a new step to a task."""
    task = load_yaml(task_path)

    if "steps" not in task:
        task["steps"] = []

    step_id = get_next_step_id(task["steps"])

    step = {
        "id": step_id,
        "action": action,
        "status": "PENDING",
        "evidence": None,
    }

    if depends_on:
        step["depends_on"] = depends_on

    task["steps"].append(step)
    task["updated"] = datetime.now(timezone.utc).isoformat()

    save_yaml(task_path, task)

    return step


def list_steps(task_path: Path) -> list:
    """List all steps in a task."""
    task = load_yaml(task_path)
    return task.get("steps", [])


def update_step_status(task_path: Path, step_id: str, status: str,
                       evidence: str = None) -> dict | None:
    """Update a step's status."""
    task = load_yaml(task_path)

    for step in task.get("steps", []):
        if step.get("id") == step_id:
            step["status"] = status
            if evidence:
                step["evidence"] = {
                    "note": evidence,
                    "at": datetime.now(timezone.utc).isoformat(),
                }

            task["updated"] = datetime.now(timezone.utc).isoformat()
            save_yaml(task_path, task)
            return step

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Add steps to tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("task_id", help="Task ID (e.g., TASK-005)")
    parser.add_argument("action", nargs="?", help="Step action description")
    parser.add_argument("--depends-on", nargs="+",
                        help="Step IDs this depends on (e.g., STEP-01)")
    parser.add_argument("--list", action="store_true",
                        help="List all steps")
    parser.add_argument("--complete", metavar="STEP_ID",
                        help="Mark step as DONE")
    parser.add_argument("--start", metavar="STEP_ID",
                        help="Mark step as IN_PROGRESS")
    parser.add_argument("--skip", metavar="STEP_ID",
                        help="Mark step as SKIPPED")
    parser.add_argument("--evidence",
                        help="Evidence note for status update")

    args = parser.parse_args()

    # Find task file
    task_path = ACTIVE_DIR / f"{args.task_id}.yaml"
    if not task_path.exists():
        print(f"{RED}Task not found: {args.task_id}{NC}")
        return 1

    # List steps
    if args.list:
        steps = list_steps(task_path)
        if not steps:
            print(f"{YELLOW}No steps defined for {args.task_id}{NC}")
            return 0

        print(f"\n{YELLOW}Steps for {args.task_id}{NC}")
        print("=" * 50)
        for step in steps:
            status = step.get("status", "?")
            icon = {
                "PENDING": "○",
                "IN_PROGRESS": "◐",
                "DONE": "●",
                "SKIPPED": "○",
            }.get(status, "?")
            deps = step.get("depends_on", [])
            deps_str = f" (after {', '.join(deps)})" if deps else ""
            print(f"  {icon} {step['id']}: {step['action']}{deps_str}")
        return 0

    # Complete a step
    if args.complete:
        step = update_step_status(task_path, args.complete, "DONE", args.evidence)
        if step:
            print(f"{GREEN}Completed: {args.complete}{NC}")
        else:
            print(f"{RED}Step not found: {args.complete}{NC}")
        return 0

    # Start a step
    if args.start:
        step = update_step_status(task_path, args.start, "IN_PROGRESS", args.evidence)
        if step:
            print(f"{YELLOW}Started: {args.start}{NC}")
        else:
            print(f"{RED}Step not found: {args.start}{NC}")
        return 0

    # Skip a step
    if args.skip:
        step = update_step_status(task_path, args.skip, "SKIPPED", args.evidence)
        if step:
            print(f"{CYAN}Skipped: {args.skip}{NC}")
        else:
            print(f"{RED}Step not found: {args.skip}{NC}")
        return 0

    # Add a new step
    if args.action:
        step = add_step(task_path, args.action, args.depends_on)
        print(f"{GREEN}Added: {step['id']} - {step['action']}{NC}")
        return 0

    # No action specified
    parser.print_help()
    return 1


if __name__ == "__main__":
    exit(main())
