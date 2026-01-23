#!/usr/bin/env python3
"""
promote_opportunity.py - Promote an opportunity from inbox to active task.

Usage:
    ./promote_opportunity.py <opportunity-file> [task-id]

Example:
    ./promote_opportunity.py OPP-001.yaml
    ./promote_opportunity.py OPP-001.yaml TASK-125

If task-id is not provided, generates next available ID.
"""

import sys
import yaml
import re
from pathlib import Path
from datetime import datetime, timezone

# Paths
SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
INBOX_DIR = AGENT_DIR / "registry" / "inbox"
ACTIVE_DIR = AGENT_DIR / "registry" / "active"

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


def usage():
    print(__doc__)
    sys.exit(1)


def find_next_task_id() -> str:
    """Find the next available TASK-XXX ID."""
    existing = list(ACTIVE_DIR.glob("TASK-*.yaml"))
    if not existing:
        return "TASK-002"  # Start after bootstrap tasks

    numbers = []
    for f in existing:
        match = re.search(r'TASK-(\d+)', f.name)
        if match:
            numbers.append(int(match.group(1)))

    next_num = max(numbers) + 1 if numbers else 2
    return f"TASK-{next_num:03d}"


def urgency_to_confidence(urgency: str) -> int:
    """Map urgency level to initial confidence score."""
    mapping = {
        "CRITICAL": 90,
        "HIGH": 80,
        "MEDIUM": 70,
        "LOW": 60,
    }
    return mapping.get(urgency.upper(), 70)


def promote(opp_file: Path, task_id: str = None):
    """Promote an opportunity to a task."""

    # Load opportunity
    with open(opp_file) as f:
        opp = yaml.safe_load(f)

    # Generate task ID if not provided
    if not task_id:
        task_id = find_next_task_id()

    task_file = ACTIVE_DIR / f"{task_id}.yaml"

    if task_file.exists():
        print(f"{RED}ERROR: Task already exists: {task_file}{NC}")
        sys.exit(1)

    print(f"{YELLOW}Promoting opportunity to task...{NC}")
    print(f"  Source: {opp_file}")
    print(f"  Target: {task_file}")

    # Extract fields
    opp_id = opp.get("id", "UNKNOWN")
    title = opp.get("title", "Untitled")
    description = opp.get("description", "")
    urgency = opp.get("urgency", "MEDIUM")
    suggested_action = opp.get("suggested_action", "")
    related_to = opp.get("related_to", [])

    confidence = urgency_to_confidence(urgency)
    now = datetime.now(timezone.utc).isoformat()

    # Build full description
    full_description = description.strip()
    if suggested_action:
        full_description += f"\n\nSuggested action: {suggested_action}"
    full_description += f"\n\n---\nPromoted from: {opp_id}\nOriginal urgency: {urgency}"

    # Create task
    task = {
        "id": task_id,
        "title": title,
        "status": "DISCOVERY",
        "description": full_description,
        "confidence": {
            "factual": confidence,
            "alignment": confidence,
            "current": confidence,
            "onwards": confidence,
            "verdict": confidence,
        },
        "tracking": {
            "created_at": now,
            "promoted_from": opp_id,
        },
        "related_to": related_to,
        "steps_completed": [],
        "output_artifacts": [],
    }

    # Write task file with header comment
    with open(task_file, 'w') as f:
        f.write(f"# Task promoted from opportunity {opp_id}\n")
        f.write(f"# Created: {now}\n\n")
        yaml.dump(task, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Update opportunity with promotion info
    opp["promoted_to"] = task_id
    opp["promoted_at"] = now

    with open(opp_file, 'w') as f:
        yaml.dump(opp, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print()
    print(f"{GREEN}SUCCESS: Created {task_file}{NC}")
    print()
    print("Next steps:")
    print(f"  1. Review and refine the task: {task_file}")
    print("  2. Score 4D confidence properly")
    print("  3. Add to sprint if appropriate")
    print(f"  4. Claim task when ready: ./claim_task.sh {task_id}")


def main():
    if len(sys.argv) < 2:
        usage()

    opp_path = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Resolve path
    opp_file = Path(opp_path)
    if not opp_file.is_absolute():
        # Try inbox directory first
        inbox_path = INBOX_DIR / opp_path
        if inbox_path.exists():
            opp_file = inbox_path
        elif not opp_file.exists():
            print(f"{RED}ERROR: Opportunity file not found: {opp_path}{NC}")
            sys.exit(1)

    if not opp_file.exists():
        print(f"{RED}ERROR: File not found: {opp_file}{NC}")
        sys.exit(1)

    promote(opp_file, task_id)


if __name__ == "__main__":
    main()
