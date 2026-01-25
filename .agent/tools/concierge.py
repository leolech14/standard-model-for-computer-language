#!/usr/bin/env python3
"""
Concierge: Context-aware agent boot system.

Replaces the 10-doc cascade with a single intelligent entry point.
Outputs everything an agent needs to start working immediately.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_git_status():
    """Get current git state."""
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        uncommitted = len([l for l in status.split('\n') if l.strip()]) if status else 0

        return {
            "branch": branch,
            "uncommitted": uncommitted,
            "clean": uncommitted == 0
        }
    except Exception:
        return {"branch": "unknown", "uncommitted": 0, "clean": True}


def get_meters():
    """Read current meter values."""
    meters_path = Path(__file__).parent.parent / "state" / "meters.yaml"
    if meters_path.exists():
        try:
            import yaml
            with open(meters_path) as f:
                data = yaml.safe_load(f)
                return data.get("meters", {})
        except Exception:
            pass
    return {"focus": 5, "reliable": 5, "debt": 2, "discovery": 5}


def get_active_task():
    """Get the most recent active task."""
    active_dir = Path(__file__).parent.parent / "registry" / "active"
    if active_dir.exists():
        tasks = sorted(active_dir.glob("TASK-*.yaml"), reverse=True)
        if tasks:
            try:
                import yaml
                with open(tasks[0]) as f:
                    data = yaml.safe_load(f)
                    return {
                        "id": tasks[0].stem,
                        "title": data.get("title", "Unknown"),
                        "status": data.get("status", "unknown")
                    }
            except Exception:
                pass
    return None


def get_inbox_count():
    """Count opportunities in inbox."""
    inbox_dir = Path(__file__).parent.parent / "registry" / "inbox"
    if inbox_dir.exists():
        return len(list(inbox_dir.glob("OPP-*.yaml")))
    return 0


def get_inbox_preview(limit=3):
    """Get preview of top inbox items (not yet promoted)."""
    inbox_dir = Path(__file__).parent.parent / "registry" / "inbox"
    items = []
    if inbox_dir.exists():
        try:
            import yaml
            for opp_file in sorted(inbox_dir.glob("OPP-*.yaml"))[:limit * 2]:
                with open(opp_file) as f:
                    data = yaml.safe_load(f)
                    # Skip already promoted
                    if data.get("promoted_to"):
                        continue
                    items.append({
                        "id": data.get("id", opp_file.stem),
                        "title": data.get("title", "Unknown")[:40],
                        "urgency": data.get("urgency", "MEDIUM")
                    })
                    if len(items) >= limit:
                        break
        except Exception:
            pass
    return items


def render_output(git, meters, task, inbox_count, inbox_preview):
    """Render the concierge output."""

    # Status line
    if git["clean"]:
        status = f"{GREEN}Ready{RESET}"
    else:
        status = f"{YELLOW}{git['uncommitted']} uncommitted{RESET}"

    # Meter bar
    def get_val(m):
        """Extract value from meter (handles dict or int)."""
        if isinstance(m, dict):
            return m.get('value', 5)
        return m

    f = get_val(meters.get('focus', 5))
    r = get_val(meters.get('reliable', 5))
    d = get_val(meters.get('debt', 2))
    meters_line = f"{CYAN}F:{f}{RESET} {GREEN}R:{r}{RESET} {RED}D:{d}{RESET}"

    # Value proposition
    print(f"""
{BOLD}╔══════════════════════════════════════════════════════════════╗
║  PROJECT ELEMENTS                                    v2.1     ║
╠══════════════════════════════════════════════════════════════╣{RESET}
║  {DIM}WHY:{RESET} See code as ARCHITECTURE, not text.                    ║
║  {DIM}HOW:{RESET} Collider analyzes → you act on structured insights.    ║
╠══════════════════════════════════════════════════════════════╣
║  {DIM}Status:{RESET} {status}
║  {DIM}Branch:{RESET} {git['branch']}
║  {DIM}Meters:{RESET} {meters_line}
║                                                              ║""")

    # Options
    print(f"║  {BOLD}YOUR OPTIONS:{RESET}                                              ║")

    if task:
        print(f"║  {CYAN}[1]{RESET} Resume {task['id']}: \"{task['title'][:30]}...\"")

    print(f"║  {CYAN}[2]{RESET} Pick from inbox ({inbox_count} total)")

    # Show inbox preview
    if inbox_preview:
        for item in inbox_preview:
            urgency_color = RED if item['urgency'] == 'HIGH' else YELLOW
            print(f"║      {urgency_color}•{RESET} {item['id']}: {item['title']}")

    print(f"║  {CYAN}[3]{RESET} Start fresh - describe your task")
    print(f"║  {YELLOW}[D]{RESET} Deal cards (Decision Deck)")
    print(f"║  {DIM}[?]{RESET} Show tutorial (--tutorial)")

    print(f"""║                                                              ║
║  {RED}{BOLD}RULES (Priority 0):{RESET}                                         ║
║  {RED}•{RESET} Never leave uncommitted changes                          ║
║  {RED}•{RESET} Run tests before claiming done                           ║
║  {RED}•{RESET} Provide summary with rationale                           ║
║                                                              ║
{BOLD}╚══════════════════════════════════════════════════════════════╝{RESET}
""")


def render_json(git, meters, task, inbox_count, inbox_preview):
    """Render JSON output for programmatic use."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "git": git,
        "meters": meters,
        "active_task": task,
        "inbox_count": inbox_count,
        "inbox_preview": inbox_preview,
        "value_proposition": {
            "why": "See code as ARCHITECTURE, not text",
            "how": "Collider analyzes → you act on structured insights"
        },
        "rules": {
            "p0": [
                "Never leave uncommitted changes",
                "Run tests before claiming done",
                "Provide summary with rationale"
            ]
        },
        "commands": {
            "analyze": "./collider full <path> --output <dir>",
            "test": "cd standard-model-of-code && pytest tests/ -q",
            "ai": "doppler run -- python context-management/tools/ai/analyze.py"
        }
    }
    print(json.dumps(output, indent=2))


def show_deck():
    """Show the Decision Deck."""
    deck_script = Path(__file__).parent / "deal_cards_ui.py"
    if deck_script.exists():
        subprocess.run([sys.executable, str(deck_script), "--chill"])
    else:
        print(f"{RED}Decision Deck not found at {deck_script}{RESET}")
        print(f"Run: python .agent/tools/deal_cards_ui.py --chill")


def main():
    """Main entry point."""
    # Parse args
    json_mode = "--json" in sys.argv
    tutorial_mode = "--tutorial" in sys.argv
    deck_mode = "--deck" in sys.argv or "-d" in sys.argv

    if deck_mode:
        show_deck()
        return

    if tutorial_mode:
        print(f"""
{BOLD}TUTORIAL MODE{RESET}

{CYAN}Step 1:{RESET} Pick a task
  - Choose from inbox or describe what you want

{CYAN}Step 2:{RESET} Make changes
  - Edit files, run commands

{CYAN}Step 3:{RESET} Validate
  - Run tests: pytest tests/ -q
  - Check status: git status

{CYAN}Step 4:{RESET} Commit
  - git add <files>
  - git commit -m "type(scope): description"

{CYAN}Step 5:{RESET} Done
  - Provide summary of what changed and why

{DIM}For deep docs: context-management/docs/deep/{RESET}
""")
        return

    # Gather state
    git = get_git_status()
    meters = get_meters()
    task = get_active_task()
    inbox_count = get_inbox_count()
    inbox_preview = get_inbox_preview(3)

    if json_mode:
        render_json(git, meters, task, inbox_count, inbox_preview)
    else:
        render_output(git, meters, task, inbox_count, inbox_preview)


if __name__ == "__main__":
    main()
