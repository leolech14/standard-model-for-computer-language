#!/usr/bin/env python3
"""
Update Task Hierarchy - Add hierarchy fields to existing tasks.

Reads all tasks in active/ and updates them with:
- sprint_id: Reference to parent sprint (from sprint task lists)
- risk: A, A+, or A++ (based on confidence)
- steps: Empty steps array if missing

Usage:
    ./update_task_hierarchy.py              # Update all tasks
    ./update_task_hierarchy.py --dry-run    # Preview changes
    ./update_task_hierarchy.py --task TASK-005  # Update specific task
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from utils.yaml_utils import load_yaml_preserve as load_yaml, save_yaml_preserve as save_yaml

SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
ACTIVE_DIR = AGENT_DIR / "registry" / "active"
SPRINTS_DIR = AGENT_DIR / "sprints"

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def build_sprint_task_map() -> dict:
    """Build map of task_id -> sprint_id from sprint files."""
    task_to_sprint = {}

    for sprint_file in SPRINTS_DIR.glob("SPRINT-*.yaml"):
        sprint = load_yaml(sprint_file)
        sprint_id = sprint.get("id")

        for task_ref in sprint.get("tasks", []):
            # Handle both "TASK-007" and {"id": "TASK-007"} formats
            if isinstance(task_ref, dict):
                task_id = task_ref.get("id")
            else:
                task_id = str(task_ref)

            if task_id:
                task_to_sprint[task_id] = sprint_id

    return task_to_sprint


def get_risk_from_confidence(confidence: dict) -> str:
    """Determine risk level based on confidence scores."""
    if isinstance(confidence, dict):
        scores = [confidence.get(k, 0) for k in ['factual', 'alignment', 'current', 'onwards'] if confidence.get(k)]
        min_score = min(scores) if scores else 0
    else:
        min_score = 0

    # Higher confidence = lower risk needed, but default to A
    # Tasks with 99%+ confidence are mission-critical (A++)
    # Tasks with 95%+ are important (A+)
    # Standard tasks are A
    if min_score >= 99:
        return "A++"
    elif min_score >= 95:
        return "A+"
    else:
        return "A"


def update_task(task_path: Path, task_to_sprint: dict, dry_run: bool = False) -> dict:
    """Update a single task with hierarchy fields."""
    task = load_yaml(task_path)
    task_id = task.get("id")
    changes = []

    # Add sprint_id if missing and we know the sprint
    if "sprint_id" not in task and task_id in task_to_sprint:
        task["sprint_id"] = task_to_sprint[task_id]
        changes.append(f"sprint_id={task_to_sprint[task_id]}")

    # Add risk if missing
    if "risk" not in task:
        confidence = task.get("confidence", {})
        risk = get_risk_from_confidence(confidence)
        task["risk"] = risk
        changes.append(f"risk={risk}")

    # Add steps if missing
    if "steps" not in task:
        task["steps"] = []
        changes.append("steps=[]")

    # Add blocked_by and blocks if missing
    if "blocked_by" not in task:
        task["blocked_by"] = []
        changes.append("blocked_by=[]")

    if "blocks" not in task:
        task["blocks"] = []
        changes.append("blocks=[]")

    # Update timestamp
    if changes:
        task["updated"] = datetime.now(timezone.utc).isoformat()

    # Save if not dry run
    if changes and not dry_run:
        save_yaml(task_path, task)

    return {
        "task_id": task_id,
        "changes": changes,
        "path": str(task_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Update tasks with hierarchy fields",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without saving")
    parser.add_argument("--task",
                        help="Update specific task ID only")

    args = parser.parse_args()

    print(f"\n{YELLOW}UPDATE TASK HIERARCHY{NC}")
    print("=" * 50)

    # Build sprint -> task map
    task_to_sprint = build_sprint_task_map()
    print(f"Found {len(task_to_sprint)} tasks mapped to sprints")
    print()

    # Get tasks to process
    if args.task:
        task_files = list(ACTIVE_DIR.glob(f"{args.task}.yaml"))
        if not task_files:
            print(f"{RED}Task not found: {args.task}{NC}")
            return
    else:
        task_files = sorted(ACTIVE_DIR.glob("TASK-*.yaml"))

    print(f"Processing {len(task_files)} tasks...")
    print()

    updated = 0
    unchanged = 0

    for task_file in task_files:
        result = update_task(task_file, task_to_sprint, args.dry_run)

        if result["changes"]:
            status = f"{CYAN}[DRY]{NC}" if args.dry_run else f"{GREEN}[UPD]{NC}"
            print(f"  {status} {result['task_id']}: {', '.join(result['changes'])}")
            updated += 1
        else:
            unchanged += 1

    print()
    print("=" * 50)
    print(f"Updated: {updated}")
    print(f"Unchanged: {unchanged}")

    if args.dry_run:
        print(f"\n{CYAN}[DRY RUN] No files were modified{NC}")


if __name__ == "__main__":
    main()
