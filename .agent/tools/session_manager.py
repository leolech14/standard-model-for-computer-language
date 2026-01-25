#!/usr/bin/env python3
"""
Session Manager - Persistence layer for Decision Deck sessions.

Manages session.yaml lifecycle:
- init_session(): Create new session
- get_session(): Read current session
- claim_task(): Set active task
- log_card_play(): Record card play with timestamp
- update_meters(): Update meters.yaml with deltas
- end_session(): Mark session complete
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

# Constants
SESSION_STALE_HOURS = 24


def get_project_root() -> Path:
    """Find PROJECT_elements root."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / ".agent").exists():
            return current
        current = current.parent
    return Path.home() / "PROJECTS_all" / "PROJECT_elements"


def get_session_path() -> Path:
    """Get path to session.yaml."""
    return get_project_root() / ".agent" / "state" / "session.yaml"


def get_meters_path() -> Path:
    """Get path to meters.yaml."""
    return get_project_root() / ".agent" / "state" / "meters.yaml"


def now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_task_counts() -> tuple[int, int]:
    """Count tasks in active and inbox directories."""
    root = get_project_root()
    active_dir = root / ".agent" / "registry" / "active"
    inbox_dir = root / ".agent" / "registry" / "inbox"

    active = len(list(active_dir.glob("*.yaml"))) if active_dir.exists() else 0
    inbox = len(list(inbox_dir.glob("*.yaml"))) if inbox_dir.exists() else 0
    return active, inbox


def get_active_sprint() -> str | None:
    """Find active sprint ID."""
    root = get_project_root()
    sprints_dir = root / ".agent" / "sprints"

    for sprint_file in sprints_dir.glob("SPRINT-*.yaml"):
        try:
            with open(sprint_file) as f:
                data = yaml.safe_load(f)
                if data.get("status") in ["EXECUTING", "ACTIVE"]:
                    return sprint_file.stem
        except Exception:
            pass
    return None


def get_meters() -> dict:
    """Read current meter values."""
    meters_path = get_meters_path()
    defaults = {"focus": 5, "reliability": 5, "debt": 2, "discovery": 5}

    if not meters_path.exists():
        return defaults

    try:
        with open(meters_path) as f:
            data = yaml.safe_load(f)
            meters = data.get("meters", {})
            return {
                "focus": meters.get("focus", {}).get("value", 5),
                "reliability": meters.get("reliability", {}).get("value", 5),
                "debt": meters.get("debt", {}).get("value", 2),
                "discovery": meters.get("discovery", {}).get("value", 5),
            }
    except Exception:
        return defaults


# === Core API ===


def get_session() -> dict | None:
    """Read current session or return None if not exists/stale."""
    session_path = get_session_path()

    if not session_path.exists():
        return None

    try:
        with open(session_path) as f:
            session = yaml.safe_load(f)

        # Check staleness
        created = datetime.fromisoformat(session.get("created_at", "").replace("Z", "+00:00"))
        age_hours = (datetime.now(timezone.utc) - created).total_seconds() / 3600

        if age_hours > SESSION_STALE_HOURS:
            return None  # Stale session

        return session
    except Exception:
        return None


def init_session(force: bool = False) -> dict:
    """Create new session. Returns session dict."""
    session_path = get_session_path()

    # Check for existing session
    if not force and session_path.exists():
        existing = get_session()
        if existing and existing.get("status") == "ACTIVE":
            return existing

    # Build session state
    active_count, inbox_count = get_task_counts()
    sprint = get_active_sprint()
    meters = get_meters()
    now = now_iso()
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    session = {
        "session_id": session_id,
        "status": "ACTIVE",
        "created_at": now,
        "last_updated": now,
        "claimed_task": None,
        "claimed_at": None,
        "cards_played": [],
        "meters_at_start": meters,
        "context": {
            "sprint": sprint,
            "inbox_count": inbox_count,
            "active_count": active_count,
        },
    }

    # Ensure state directory exists
    session_path.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write
    with open(session_path, "w") as f:
        yaml.dump(session, f, default_flow_style=False, sort_keys=False)

    return session


def claim_task(task_id: str) -> dict:
    """Set claimed_task in session. Returns updated session."""
    session = get_session()
    if not session:
        session = init_session()

    session["claimed_task"] = task_id
    session["claimed_at"] = now_iso()
    session["last_updated"] = now_iso()

    with open(get_session_path(), "w") as f:
        yaml.dump(session, f, default_flow_style=False, sort_keys=False)

    return session


def unclaim_task() -> dict:
    """Clear claimed_task. Returns updated session."""
    session = get_session()
    if not session:
        session = init_session()

    session["claimed_task"] = None
    session["claimed_at"] = None
    session["last_updated"] = now_iso()

    with open(get_session_path(), "w") as f:
        yaml.dump(session, f, default_flow_style=False, sort_keys=False)

    return session


def log_card_play(card_id: str, outcome: str = "success", context: str | None = None) -> dict:
    """Append card play to session history. Returns updated session."""
    session = get_session()
    if not session:
        session = init_session()

    play = {
        "card_id": card_id,
        "played_at": now_iso(),
        "outcome": outcome,
    }
    if context:
        play["context"] = context

    session["cards_played"].append(play)
    session["last_updated"] = now_iso()

    with open(get_session_path(), "w") as f:
        yaml.dump(session, f, default_flow_style=False, sort_keys=False)

    return session


def update_meters(deltas: dict, reason: str = "Card played") -> dict:
    """Update meters.yaml with deltas. Returns new meter values."""
    meters_path = get_meters_path()
    now = now_iso()

    # Read current state
    if meters_path.exists():
        with open(meters_path) as f:
            data = yaml.safe_load(f)
    else:
        data = {
            "version": "1.0",
            "last_updated": now,
            "meters": {
                name: {"value": 5, "max": 10, "description": "", "history": []}
                for name in ["focus", "reliability", "debt", "discovery"]
            },
            "thresholds": {"critical": 2, "low": 4, "normal": 6, "high": 8, "excellent": 10},
        }

    # Apply deltas
    meters = data.get("meters", {})
    for name, delta in deltas.items():
        if name in meters:
            old_value = meters[name].get("value", 5)
            new_value = max(0, min(10, old_value + delta))
            meters[name]["value"] = new_value

            # Add history entry
            if "history" not in meters[name]:
                meters[name]["history"] = []
            meters[name]["history"].append({
                "timestamp": now,
                "delta": delta,
                "reason": reason,
            })

    data["meters"] = meters
    data["last_updated"] = now

    with open(meters_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return {name: m.get("value", 5) for name, m in meters.items()}


def end_session(status: str = "COMPLETE") -> dict:
    """Mark session as complete. Returns final session state."""
    session = get_session()
    if not session:
        return {"error": "No active session"}

    session["status"] = status
    session["last_updated"] = now_iso()
    session["ended_at"] = now_iso()

    with open(get_session_path(), "w") as f:
        yaml.dump(session, f, default_flow_style=False, sort_keys=False)

    return session


def show_session():
    """Display current session state."""
    session = get_session()
    if not session:
        print("No active session. Run: session_manager.py init")
        return

    print(f"\n  SESSION: {session['session_id']}")
    print(f"  Status: {session['status']}")
    print(f"  Created: {session['created_at']}")

    task = session.get("claimed_task")
    if task:
        print(f"  Task: {task} (since {session.get('claimed_at', '?')})")
    else:
        print("  Task: (none claimed)")

    cards = session.get("cards_played", [])
    if cards:
        print(f"  Cards played: {len(cards)}")
        for c in cards[-3:]:  # Last 3
            print(f"    - {c['card_id']} ({c['outcome']})")

    meters = get_meters()
    print(f"  Meters: f:{meters['focus']} r:{meters['reliability']} d:{meters['debt']} disc:{meters['discovery']}")
    print()


# === CLI ===


def main():
    if len(sys.argv) < 2:
        print("Usage: session_manager.py <command> [args]")
        print("Commands: init, show, claim <task>, unclaim, log <card> [outcome], meters <json>, end")
        return

    cmd = sys.argv[1]

    if cmd == "init":
        force = "--force" in sys.argv
        session = init_session(force=force)
        print(f"Session initialized: {session['session_id']}")

    elif cmd == "show":
        show_session()

    elif cmd == "claim":
        if len(sys.argv) < 3:
            print("Usage: session_manager.py claim <task_id>")
            return
        task_id = sys.argv[2]
        session = claim_task(task_id)
        print(f"Claimed: {task_id}")

    elif cmd == "unclaim":
        session = unclaim_task()
        print("Task unclaimed")

    elif cmd == "log":
        if len(sys.argv) < 3:
            print("Usage: session_manager.py log <card_id> [outcome] [context]")
            return
        card_id = sys.argv[2]
        outcome = sys.argv[3] if len(sys.argv) > 3 else "success"
        context = sys.argv[4] if len(sys.argv) > 4 else None
        session = log_card_play(card_id, outcome, context)
        print(f"Logged: {card_id} ({outcome})")

    elif cmd == "meters":
        if len(sys.argv) < 3:
            print("Usage: session_manager.py meters '{\"focus\": 1, \"reliability\": -1}'")
            return
        import json
        deltas = json.loads(sys.argv[2])
        reason = sys.argv[3] if len(sys.argv) > 3 else "Manual update"
        meters = update_meters(deltas, reason)
        print(f"Meters updated: {meters}")

    elif cmd == "end":
        status = sys.argv[2] if len(sys.argv) > 2 else "COMPLETE"
        session = end_session(status)
        print(f"Session ended: {session.get('session_id', '?')}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
