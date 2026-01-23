#!/usr/bin/env python3
"""
PRIORITY MATRIX - The Billboard

A real-time dashboard showing the state of all orders in the repo.
Designed to be run frequently and give instant situational awareness.

Usage:
    python priority_matrix.py           # Full billboard
    python priority_matrix.py --compact # One-line summary
    python priority_matrix.py --json    # Machine-readable

The Billboard shows:
- Active TASKs by status (READY, IN_PROGRESS, BLOCKED, DONE)
- Inbox funnel (A+/A/B/C/F grade distribution)
- Sprint progress
- Top priorities for immediate action
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent paths for shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "context-management" / "tools" / "ai"))

# Paths
AGENT_DIR = Path(__file__).parent.parent
ACTIVE_DIR = AGENT_DIR / "registry" / "active"
INBOX_DIR = AGENT_DIR / "registry" / "inbox"
SPRINTS_DIR = AGENT_DIR / "sprints"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"

# Status colors
STATUS_COLORS = {
    "READY": GREEN,
    "IN_PROGRESS": YELLOW,
    "BLOCKED": RED,
    "DONE": DIM,
    "COMPLETED": DIM,
    "PENDING": CYAN,
}

# Priority colors
PRIORITY_COLORS = {
    "P0": f"{BG_RED}{WHITE}",
    "P1": RED,
    "P2": YELLOW,
    "P3": CYAN,
}

# Grade thresholds (same as industrial_triage.py)
GRADES = {"A+": 95, "A": 85, "B": 70, "C": 50, "F": 0}


def load_tasks() -> List[Dict]:
    """Load all TASK-*.yaml from active directory."""
    tasks = []
    if not ACTIVE_DIR.exists():
        return tasks

    for task_file in sorted(ACTIVE_DIR.glob("TASK-*.yaml")):
        try:
            with open(task_file) as f:
                task = yaml.safe_load(f)
                if task:
                    task["_file"] = task_file.name
                    tasks.append(task)
        except Exception as e:
            print(f"Warning: Failed to load {task_file}: {e}", file=sys.stderr)

    return tasks


def load_opportunities() -> List[Dict]:
    """Load all OPP-*.yaml from inbox."""
    opps = []
    if not INBOX_DIR.exists():
        return opps

    for opp_file in sorted(INBOX_DIR.glob("OPP-*.yaml")):
        try:
            with open(opp_file) as f:
                opp = yaml.safe_load(f)
                if opp:
                    opp["_file"] = opp_file.name
                    opps.append(opp)
        except Exception:
            pass

    return opps


def load_current_sprint() -> Optional[Dict]:
    """Load the most recent sprint file."""
    if not SPRINTS_DIR.exists():
        return None

    sprint_files = sorted(SPRINTS_DIR.glob("SPRINT-*.yaml"), reverse=True)
    if sprint_files:
        try:
            with open(sprint_files[0]) as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    return None


def compute_grade(opp: Dict) -> str:
    """Compute grade for an opportunity based on confidence."""
    conf = opp.get("confidence", {})
    factual = conf.get("factual", 50)
    alignment = conf.get("alignment", 50)
    current = conf.get("current", 50)
    onwards = conf.get("onwards", 50)
    overall = min(factual, alignment, current, onwards)

    for grade, threshold in sorted(GRADES.items(), key=lambda x: -x[1]):
        if overall >= threshold:
            return grade
    return "F"


def categorize_tasks(tasks: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize tasks by status."""
    categories = {
        "READY": [],
        "IN_PROGRESS": [],
        "BLOCKED": [],
        "DONE": [],
    }

    for task in tasks:
        status = task.get("status", "READY").upper()
        if status in ["COMPLETED", "DONE"]:
            categories["DONE"].append(task)
        elif status == "BLOCKED":
            categories["BLOCKED"].append(task)
        elif status == "IN_PROGRESS":
            categories["IN_PROGRESS"].append(task)
        else:
            categories["READY"].append(task)

    return categories


def categorize_inbox(opps: List[Dict]) -> Dict[str, int]:
    """Categorize inbox by grade."""
    grades = {"A+": 0, "A": 0, "B": 0, "C": 0, "F": 0}
    for opp in opps:
        grade = compute_grade(opp)
        grades[grade] = grades.get(grade, 0) + 1
    return grades


def get_top_priorities(tasks: List[Dict], limit: int = 5) -> List[Dict]:
    """Get top priority tasks that are actionable."""
    actionable = [t for t in tasks if t.get("status", "").upper() in ["READY", "IN_PROGRESS"]]

    def priority_key(t):
        p = t.get("priority", "P2")
        return {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(p, 2)

    return sorted(actionable, key=priority_key)[:limit]


def render_billboard(tasks: List[Dict], opps: List[Dict], sprint: Optional[Dict]):
    """Render the full priority matrix billboard."""
    task_cats = categorize_tasks(tasks)
    inbox_grades = categorize_inbox(opps)
    top_priorities = get_top_priorities(tasks)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Header
    print()
    print(f"{MAGENTA}{'█' * 74}{RESET}")
    print(f"{MAGENTA}█{RESET}{' ' * 72}{MAGENTA}█{RESET}")
    print(f"{MAGENTA}█{RESET}  {BOLD}{WHITE}P R I O R I T Y   M A T R I X{RESET}                                       {MAGENTA}█{RESET}")
    print(f"{MAGENTA}█{RESET}  {DIM}The Billboard - State of All Orders{RESET}                                  {MAGENTA}█{RESET}")
    print(f"{MAGENTA}█{RESET}{' ' * 72}{MAGENTA}█{RESET}")
    print(f"{MAGENTA}{'█' * 74}{RESET}")
    print(f"  {DIM}Generated: {now}{RESET}")
    print()

    # Sprint Status
    if sprint:
        sprint_id = sprint.get("id", "?")
        sprint_name = sprint.get("name", "?")[:40]
        sprint_status = sprint.get("status", "ACTIVE")
        print(f"  {CYAN}ACTIVE SPRINT{RESET}")
        print(f"  {DIM}{'─' * 70}{RESET}")
        print(f"    {BOLD}{sprint_id}{RESET}: {sprint_name} [{sprint_status}]")
        print()

    # Task Status Overview
    total_tasks = len(tasks)
    ready = len(task_cats["READY"])
    in_prog = len(task_cats["IN_PROGRESS"])
    blocked = len(task_cats["BLOCKED"])
    done = len(task_cats["DONE"])

    print(f"  {BLUE}TASK STATUS{RESET} ({total_tasks} total)")
    print(f"  {DIM}{'─' * 70}{RESET}")

    # Status bars
    bar_width = 40
    for status, count in [("READY", ready), ("IN_PROGRESS", in_prog), ("BLOCKED", blocked), ("DONE", done)]:
        color = STATUS_COLORS.get(status, WHITE)
        pct = count / max(total_tasks, 1)
        filled = int(pct * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"    {color}{status:12}{RESET} {bar} {BOLD}{count:3}{RESET}")
    print()

    # Inbox Funnel
    total_inbox = len(opps)
    print(f"  {YELLOW}INBOX FUNNEL{RESET} ({total_inbox} opportunities)")
    print(f"  {DIM}{'─' * 70}{RESET}")

    grade_colors = {"A+": GREEN, "A": GREEN, "B": YELLOW, "C": YELLOW, "F": RED}
    for grade in ["A+", "A", "B", "C", "F"]:
        count = inbox_grades[grade]
        color = grade_colors[grade]
        pct = count / max(total_inbox, 1)
        filled = int(pct * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        status_hint = "→ PROMOTE" if grade in ["A+", "A"] else "  research" if grade in ["B", "C"] else "  validate"
        print(f"    {color}{grade:3}{RESET} {bar} {BOLD}{count:3}{RESET} {DIM}{status_hint}{RESET}")
    print()

    # Top Priorities (THE ORDERS)
    print(f"  {RED}▼ TOP PRIORITIES ▼{RESET}")
    print(f"  {DIM}{'─' * 70}{RESET}")

    if top_priorities:
        for i, task in enumerate(top_priorities, 1):
            task_id = task.get("id", "?")
            title = task.get("title", "?")[:45]
            priority = task.get("priority", "P2")
            status = task.get("status", "READY").upper()

            p_color = PRIORITY_COLORS.get(priority, WHITE)
            s_color = STATUS_COLORS.get(status, WHITE)

            print(f"    {BOLD}{i}.{RESET} {p_color}[{priority}]{RESET} {task_id:10} {s_color}{status:12}{RESET} {title}")
    else:
        print(f"    {DIM}No actionable tasks{RESET}")
    print()

    # Quick Stats Footer
    promotable = inbox_grades["A+"] + inbox_grades["A"]
    needs_work = inbox_grades["B"] + inbox_grades["C"] + inbox_grades["F"]

    print(f"  {DIM}{'─' * 70}{RESET}")
    print(f"  {GREEN}▸ Ready:{RESET} {ready}  {YELLOW}▸ In Progress:{RESET} {in_prog}  {RED}▸ Blocked:{RESET} {blocked}  {DIM}▸ Done:{RESET} {done}")
    print(f"  {GREEN}▸ Promotable:{RESET} {promotable}  {YELLOW}▸ Needs Research:{RESET} {needs_work}")
    print()
    print(f"{MAGENTA}{'█' * 74}{RESET}")
    print()


def render_compact(tasks: List[Dict], opps: List[Dict]):
    """One-line summary for quick checks."""
    task_cats = categorize_tasks(tasks)
    inbox_grades = categorize_inbox(opps)

    ready = len(task_cats["READY"])
    in_prog = len(task_cats["IN_PROGRESS"])
    blocked = len(task_cats["BLOCKED"])
    promotable = inbox_grades["A+"] + inbox_grades["A"]

    print(f"{MAGENTA}[MATRIX]{RESET} Tasks: {GREEN}{ready}R{RESET}/{YELLOW}{in_prog}P{RESET}/{RED}{blocked}B{RESET} | Inbox: {GREEN}{promotable}↑{RESET}/{YELLOW}{len(opps)-promotable}?{RESET}")


def render_json(tasks: List[Dict], opps: List[Dict], sprint: Optional[Dict]):
    """Machine-readable JSON output."""
    task_cats = categorize_tasks(tasks)
    inbox_grades = categorize_inbox(opps)

    output = {
        "timestamp": datetime.now().isoformat(),
        "tasks": {
            "total": len(tasks),
            "ready": len(task_cats["READY"]),
            "in_progress": len(task_cats["IN_PROGRESS"]),
            "blocked": len(task_cats["BLOCKED"]),
            "done": len(task_cats["DONE"]),
        },
        "inbox": {
            "total": len(opps),
            "grades": inbox_grades,
            "promotable": inbox_grades["A+"] + inbox_grades["A"],
        },
        "sprint": sprint.get("id") if sprint else None,
        "top_priorities": [
            {"id": t.get("id"), "priority": t.get("priority"), "title": t.get("title")}
            for t in get_top_priorities(tasks)
        ],
    }
    print(json.dumps(output, indent=2))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Priority Matrix - The Billboard")
    parser.add_argument("--compact", "-c", action="store_true", help="One-line summary")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()

    # Load data
    tasks = load_tasks()
    opps = load_opportunities()
    sprint = load_current_sprint()

    # Render
    if args.json:
        render_json(tasks, opps, sprint)
    elif args.compact:
        render_compact(tasks, opps)
    else:
        render_billboard(tasks, opps, sprint)


if __name__ == "__main__":
    main()
