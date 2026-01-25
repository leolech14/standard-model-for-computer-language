#!/usr/bin/env python3
"""
Decision Deck - Terminal UI with Style

Compact, colorful card display with personality.
BLESSSS
"""

import sys
import os
import yaml
from pathlib import Path

# ANSI Colors
YELLOW = "\033[93m"
GREEN = "\033[92m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
WHITE = "\033[97m"
CYAN = "\033[96m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

# Card colors - each card gets its own color
CARD_COLORS = [
    CYAN,      # [1] - cyan
    MAGENTA,   # [2] - magenta
    YELLOW,    # [3] - yellow
    BLUE,      # [4] - blue
    GREEN,     # [5] - green
]
WILD_COLOR = RED  # Wildcard is always red (danger!)


def get_project_root():
    """Find PROJECT_elements root."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / ".agent").exists():
            return current
        current = current.parent
    return Path.home() / "PROJECTS_all" / "PROJECT_elements"


def get_active_sprint_phase():
    """Read active sprint and return its phase."""
    root = get_project_root()
    sprints_dir = root / ".agent" / "sprints"

    # Find EXECUTING sprint (or ACTIVE if it exists)
    for sprint_file in sprints_dir.glob("SPRINT-*.yaml"):
        try:
            with open(sprint_file) as f:
                data = yaml.safe_load(f)
                if data.get("status") in ["EXECUTING", "ACTIVE"]:
                    phase_id = data.get("phase_id", "P0")
                    return phase_id
        except Exception:
            pass

    return "PLANNING"


def phase_id_to_name(phase_id: str) -> str:
    """Convert phase ID to human-readable name."""
    phase_map = {
        "P0": "Foundation",
        "P1": "Discovery",
        "P2": "Topology",
        "P3": "Reachability",
        "P4": "Proof system",
        "P5": "Visualization",
        "P6": "Intelligence",
        "P7": "Streaming",
        "P8": "Scaling",
        "P9": "Survey",
        "P10": "Intelligence Layer",
    }
    return phase_map.get(phase_id, phase_id)


def get_task_counts():
    """Read actual task counts from registry."""
    root = get_project_root()

    active_dir = root / ".agent" / "registry" / "active"
    inbox_dir = root / ".agent" / "registry" / "inbox"

    active_count = len(list(active_dir.glob("*.yaml"))) if active_dir.exists() else 0
    inbox_count = len(list(inbox_dir.glob("*.yaml"))) if inbox_dir.exists() else 0

    return active_count, inbox_count


def get_meters():
    """Read meter values from meters.yaml."""
    root = get_project_root()
    meters_file = root / ".agent" / "state" / "meters.yaml"

    # Default values
    defaults = {
        "focus": 5,
        "reliability": 5,
        "debt": 2,
        "discovery": 5,
    }

    if not meters_file.exists():
        return defaults

    try:
        with open(meters_file) as f:
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


def get_session():
    """Read session.yaml if it exists."""
    root = get_project_root()
    session_file = root / ".agent" / "state" / "session.yaml"

    if not session_file.exists():
        return None

    try:
        with open(session_file) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def format_time_ago(iso_timestamp: str) -> str:
    """Convert ISO timestamp to human-readable 'Xm ago' format."""
    from datetime import datetime, timezone

    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - dt

        minutes = int(delta.total_seconds() / 60)
        if minutes < 1:
            return "now"
        elif minutes < 60:
            return f"{minutes}m"
        elif minutes < 1440:
            return f"{minutes // 60}h"
        else:
            return f"{minutes // 1440}d"
    except Exception:
        return "?"


def build_real_stats():
    """Build stats dict from real state including session."""
    active, inbox = get_task_counts()
    meters = get_meters()
    session = get_session()

    stats = {
        "session": "NEW",
        "task": None,
        "task_time": None,
        "inbox": inbox,
        "active": active,
        "cards_played": [],
        "insight": f"focus:{meters['focus']} | reliability:{meters['reliability']} | debt:{meters['debt']}"
    }

    if session:
        stats["session"] = session.get("status", "ACTIVE")
        stats["task"] = session.get("claimed_task")
        if session.get("claimed_at"):
            stats["task_time"] = format_time_ago(session["claimed_at"])
        stats["cards_played"] = session.get("cards_played", [])[-5:]  # Last 5

    return stats


def render_vibes(cards: list = None, phase: str = "DESIGNING"):
    """Maximum vibes, minimum space. Responsive to any width. RAINBOW."""
    if cards is None:
        cards = [
            {"short": "claim", "ready": True},
            {"short": "triage", "ready": True},
            {"short": "research", "ready": True},
        ]

    print()
    print(f"{YELLOW}♠{RESET} {BOLD}pick ur move{RESET}  {DIM}[{phase}]{RESET}")
    print()

    # Cards inline with spacing - wraps naturally, each colored
    card_line = "  "
    for i, card in enumerate(cards):
        color = get_card_color(i)
        short = card.get("short", "?")[:8]
        card_line += f"{color}[{i+1}]{RESET} {color}{short}{RESET}    "

    card_line += f"{WILD_COLOR}[W]{RESET} {WILD_COLOR}wild{RESET}"
    print(card_line)
    print()

    # Meters from real state
    meters = get_meters()
    print(f"  {DIM}f:{meters['focus']}  r:{meters['reliability']}  d:{meters['debt']}  dsc:{meters['discovery']}{RESET}")
    print()

    # The blessing
    print(f"{GREEN}  🌿 BLESSSS{RESET}")
    print()


def render_cards_horizontal(cards: list = None, phase: str = "DESIGNING"):
    """Horizontal mini cards with COLORS."""
    if cards is None:
        cards = [
            {"short": "claim", "num": 1},
            {"short": "triage", "num": 2},
            {"short": "research", "num": 3},
        ]

    print()
    print(f"{YELLOW}♠ DECK{RESET}  {DIM}{phase}{RESET}")
    print()

    # Build card rows with colors
    top = "  "
    mid = "  "
    bot = "  "

    for i, card in enumerate(cards):
        color = get_card_color(i)
        short = card.get("short", "?")[:2]
        top += f"{color}┌──────┐{RESET}  "
        mid += f"{color}│{RESET}{BOLD}[{i+1}]{RESET} {color}{short}{RESET}  {color}│{RESET}  "
        bot += f"{color}└──────┘{RESET}  "

    # Wildcard in red
    top += f"{WILD_COLOR}┌──────┐{RESET}"
    mid += f"{WILD_COLOR}│{RESET}{BOLD}[W]{RESET} {WILD_COLOR}⚡{RESET}  {WILD_COLOR}│{RESET}"
    bot += f"{WILD_COLOR}└──────┘{RESET}"

    print(top)
    print(mid)
    print(bot)
    print()

    # Meters from real state
    meters = get_meters()
    print(f"  {DIM}meters{RESET}  f:{meters['focus']}  r:{meters['reliability']}  d:{meters['debt']}  dsc:{meters['discovery']}")
    print()
    print(f"{GREEN}  🌿 BLESSSS{RESET}")
    print()


def render_mini(cards: list = None, phase: str = "DESIGNING"):
    """Tiniest possible. Two lines."""
    if cards is None:
        cards = ["claim", "triage", "research"]

    card_str = "  ".join([f"{YELLOW}[{i+1}]{RESET}{c[:5]}" for i, c in enumerate(cards)])

    # Meters from real state
    meters = get_meters()
    print()
    print(f"{YELLOW}♠{RESET} {card_str}  {YELLOW}[W]{RESET}wild  {DIM}|{RESET}  {DIM}f:{meters['focus']} r:{meters['reliability']} d:{meters['debt']}{RESET}")
    print(f"{GREEN}  🌿{RESET}")
    print()


def get_card_color(index: int) -> str:
    """Get color for card at index."""
    return CARD_COLORS[index % len(CARD_COLORS)]


def render_context(stats: dict = None):
    """Render context section with session, task, and card history."""
    if stats is None:
        stats = build_real_stats()

    print(f"  {DIM}┌─ SESSION ─────────────────────┐{RESET}")

    # Task row
    task = stats.get("task")
    task_time = stats.get("task_time")
    if task:
        time_str = f" ({task_time})" if task_time else ""
        task_display = f"{task}{time_str}"[:26]
        print(f"  {DIM}│{RESET} {CYAN}task:{RESET} {task_display:<24} {DIM}│{RESET}")
    else:
        print(f"  {DIM}│{RESET} {YELLOW}no task claimed{RESET}              {DIM}│{RESET}")

    # Cards played row
    cards = stats.get("cards_played", [])
    if cards:
        # Show abbreviated card trail: SES→REG→GIT
        card_trail = "→".join([c["card_id"].split("-")[1][:3] for c in cards[-4:]])
        card_count = len(cards)
        card_display = f"{card_trail} ({card_count})"[:26]
        print(f"  {DIM}│{RESET} {MAGENTA}cards:{RESET} {card_display:<24} {DIM}│{RESET}")

    # Stats row
    inbox = stats.get("inbox", 0)
    active = stats.get("active", 0)
    print(f"  {DIM}│{RESET} inbox:{MAGENTA}{inbox}{RESET}  active:{CYAN}{active}{RESET}           {DIM}│{RESET}")

    print(f"  {DIM}└───────────────────────────────┘{RESET}")
    print()


def render_chill(cards: list = None, phase: str = None, stats: dict = None):
    """Chill aesthetic. Clean spacing. RAINBOW CARDS + CONTEXT."""
    # Read real state if not provided
    if phase is None:
        phase_id = get_active_sprint_phase()
        phase = phase_id_to_name(phase_id)

    if stats is None:
        stats = build_real_stats()

    if cards is None:
        cards = [
            {"short": "claim", "desc": "grab a task"},
            {"short": "triage", "desc": "check inbox"},
            {"short": "research", "desc": "ask the oracle"},
        ]

    print()
    print(f"  {YELLOW}━━━ ♠ DECK ━━━{RESET}  {DIM}{phase}{RESET}")
    print()

    # Context section
    render_context(stats)

    # Cards
    for i, card in enumerate(cards):
        color = get_card_color(i)
        short = card.get("short", "?")
        desc = card.get("desc", "")
        print(f"    {color}[{i+1}]{RESET}  {color}{BOLD}{short}{RESET}  {DIM}~ {desc}{RESET}")

    print(f"    {WILD_COLOR}[W]{RESET}  {WILD_COLOR}{BOLD}wild{RESET}  {DIM}~ break the rules{RESET}")
    print()

    # Mini meters bar with real values
    meters = get_meters()
    print(f"  {DIM}────────────────────{RESET}")
    print(f"  {CYAN}▪{RESET} focus:{meters['focus']}  {MAGENTA}▪{RESET} reliable:{meters['reliability']}  {YELLOW}▪{RESET} debt:{meters['debt']}")
    print()
    print(f"  {GREEN}🌿 BLESSSS{RESET}")
    print()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--chill"

    if mode == "--vibes":
        render_vibes()
    elif mode == "--cards":
        render_cards_horizontal()
    elif mode == "--mini":
        render_mini()
    elif mode == "--chill":
        render_chill()
    else:
        print("Options: --vibes, --cards, --mini, --chill")
